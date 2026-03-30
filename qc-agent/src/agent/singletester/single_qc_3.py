# ./agent/singletester/single_qc_3.py
import json
import asyncio
from agent import AbstractAgent
from memory.shared_memory import SharedMemory
from tools.mcpclient import MCPClient
from utils.logger import Logger
import config
from pydantic import BaseModel
from contextlib import AsyncExitStack

# (Keep SINGLE_QC_AGENT_PROFILE and Reasoning class as they are)
SINGLE_QC_AGENT_PROFILE = {
    "name": "SingleQCAgent",
    "role": "Autonomous AI Quality Control Specialist",
    "target": "To sequentially execute a given test plan, handle complex multi-step tasks, verify the outcomes against expected results, and report a final status.",
    "ability": (
        "Understands a test plan, breaks down each step into actionable tool calls, "
        "executes them via an MCP client, analyzes the results, and decides if a step is "
        "complete or requires further actions. It operates in a loop until a step's "
        "goal is verifiably achieved or determined to be a failure."
    ),
    "personality": "Meticulous, persistent, and autonomous. It focuses on completing one step fully before moving to the next.",
    "constraints": [
        "Must execute steps in the provided order.",
        "Must verify the result of each step before proceeding.",
        "Must use the available tools to achieve the step's goal.",
        "If a step cannot be completed after multiple attempts, it must be marked as a failure."
    ],
    "output_format": (
        "During execution, selects a tool to call. If the step's goal is met or has failed, "
        "responds with a JSON object: {\"status\": \"SUCCESS\" or \"FAILURE\", \"reason\": \"<detailed_explanation>\"}."
    )
}

class Reasoning(BaseModel):
    status: str
    reason: str
    # 'next_step' and 'step_id' are removed as they were causing confusion.
    # The agent should only report the status and reason for the *current* step.

class SingleQCAgent(AbstractAgent):
    """
    An autonomous agent that handles the entire test execution workflow.
    It now uses a robust two-loop structure to manage state correctly.
    """

    def __init__(self, mcp_clients: list[MCPClient] = None, shared_memory: SharedMemory = None, logger: Logger = None):
        _mcp_clients = []
        if config.MCP_SERVERS_CONFIG:
            for server_name, server_config in config.MCP_SERVERS_CONFIG.items():
                print(f"Initializing MCP client for '{server_name}'...")
                _mcp_clients.append(MCPClient(server_config))

        _logger = Logger()
        super().__init__(SINGLE_QC_AGENT_PROFILE, mcp_clients=_mcp_clients, shared_memory=None, logger=_logger)

    def agent_as_a_function_description(self) -> dict:
        return {}

    async def run(self, test_plan: list[dict], max_step_attempts: int = 5) -> dict:
        self.logger.console_log(0, self.profile['name'], "Starting autonomous test execution workflow.")
        
        workflow_state = {
            "overall_status": "In Progress",
            "step_results": {},
        }

        async with AsyncExitStack() as stack:
            try:
                # Connect all MCP clients at the beginning of the workflow
                await asyncio.gather(*[stack.enter_async_context(client) for client in self.mcp_clients])

                # === OUTER LOOP: Manages which step we are on ===
                for step_index, current_step in enumerate(test_plan):
                    step_id = current_step.get("id", f"step_{step_index}")
                    self.logger.console.print(f"\n[bold blue]--- Starting Step {step_index + 1}/{len(test_plan)}: {current_step['description']} ---[/bold blue]")

                    step_action_history = []
                    step_completed = False

                    # === INNER LOOP: Tries to complete the CURRENT step ===
                    for attempt in range(1, max_step_attempts + 1):
                        log_step_index = f"{step_index+1}-{attempt}" # e.g., "1-1", "1-2", "2-1"
                        self.logger.console_log(log_step_index, self.profile['name'], f"Attempt {attempt}/{max_step_attempts} for Step {step_index+1}")

                        # 1. REASONING PHASE: Is the current step done?
                        reasoning_task = f"""
**Current Goal (From Test Plan):**
- Description: "{current_step['description']}"
- Expected Result: "{current_step['expectedResult']}"

**History of Actions Taken for THIS Goal So Far:**
{json.dumps(step_action_history, indent=2) if step_action_history else "No actions taken yet."}

**Your Task:**
Based on the **History of Actions**, determine if the **Current Goal** has been met. Analyze the provided system state from the action history.
1.  **First, determine if the Current Goal has already been met.** For example, if the goal is to "log in" and the state shows you are already logged in, the goal is met.
2.  If the goal is **already met**, respond with `status: "SUCCESS"` and a reason explaining that the step was skipped because its condition was already satisfied.
3.  If the goal has **irrecoverably failed** or is impossible, respond with `status: "FAILURE"`.
4.  If the goal is **not yet met** and more actions are needed, respond with `status: "NOT_DONE"`.
"""
                        system_prompt = self.memory.assemble_prompt(self.profile, reasoning_task)
                        reasoning: Reasoning = await self._execute_llm_call(system_prompt, reasoning_task, response_format=Reasoning)

                        self.logger.log_agent_step(
                            step_index=log_step_index, agent_name=f"{self.profile['name']}_Reasoning",
                            system_prompt=system_prompt, user_prompt=reasoning_task, llm_response=reasoning
                        )
                        
                        if reasoning.status == "SUCCESS":
                            self.logger.console.print(f"[bold green]✅ Step {step_index+1} VERIFIED as SUCCESS.[/bold green]")
                            workflow_state["step_results"][step_id] = {"status": "SUCCESS", "reason": reasoning.reason, "attempts": attempt}
                            step_completed = True
                            break # Exit inner loop, move to next step in outer loop
                        
                        if reasoning.status == "FAILURE":
                            self.logger.console.print(f"[bold red]❌ Step {step_index+1} VERIFIED as FAILURE.[/bold red]")
                            workflow_state["step_results"][step_id] = {"status": "FAILURE", "reason": reasoning.reason, "attempts": attempt}
                            step_completed = True
                            break # Exit inner loop, move to next step in outer loop

                        # 2. TOOL USE PHASE: If not done, decide the next action
                        tool_task = f"""
**Current Goal (From Test Plan):**
- Description: "{current_step['description']}"
- Expected Result: "{current_step['expectedResult']}"

**Analysis**
- Current status: {reasoning.status}
- Reason for current status: {reasoning.reason}

**History of Actions & Current System State (for THIS goal):**
{json.dumps(step_action_history, indent=2) if step_action_history else "No actions taken yet. The current state is unknown."}

**Your Task:**
Choose **one single tool** from the available tools to make progress towards the **Current Goal**.
The last action failed with 'Session terminated'. You MUST start by re-establishing the browser session by navigating to the required URL before doing anything else.
"""
                        system_prompt = self.memory.assemble_prompt(self.profile, tool_task)
                        llm_response = await self._execute_llm_call(system_prompt, tool_task, use_tool=True, tool_choice='auto')

                        if not llm_response or not llm_response.choices[0].message.tool_calls:
                            self.logger.console.print("[bold red]LLM failed to select a tool. Ending step.[/bold red]")
                            step_action_history.append({"status": "error", "details": "LLM did not choose a tool."})
                            continue # try the next attempt

                        tool_call = llm_response.choices[0].message.tool_calls[0]
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        self.logger.console_log(log_step_index, "ToolCall", f"Executing: {tool_name}({json.dumps(tool_args)})")
                        
                        # Find the right MCP client for the tool
                        mcp_client = self.map_tool_mcp.get(tool_name)
                        if not mcp_client:
                            error_msg = f"No MCP client found for tool '{tool_name}'"
                            self.logger.console.print(f"[bold red]{error_msg}[/bold red]")
                            execution_result = {"status": "error", "details": error_msg}
                        else:
                            execution_result = await mcp_client.execute_tool(tool_name, tool_args)
                        
                        step_action_history.append(execution_result) # Add result to this step's history
                        
                        self.logger.log_agent_step(
                            step_index=log_step_index, agent_name=f"{self.profile['name']}_ToolUse",
                            system_prompt=system_prompt, user_prompt=tool_task, llm_response=llm_response.choices[0].message,
                            tool_responses=[execution_result]
                        )

                    # After inner loop, check if the step was completed
                    if not step_completed:
                        self.logger.console.print(f"[bold red]❌ Step {step_index+1} FAILED after {max_step_attempts} attempts.[/bold red]")
                        workflow_state["step_results"][step_id] = {
                            "status": "FAILURE",
                            "reason": f"Max attempts ({max_step_attempts}) reached without success.",
                            "attempts": max_step_attempts,
                        }
                        workflow_state["overall_status"] = "Failed"
                        self.logger.console.print("[bold red]Workflow terminated due to step failure.[/bold red]")
                        return workflow_state # Terminate the entire workflow
            except Exception as e:
                print(f"Exception : {e}")

        all_steps_succeeded = all(res['status'] == 'SUCCESS' for res in workflow_state['step_results'].values())
        workflow_state["overall_status"] = "Success" if all_steps_succeeded else "Failed"
        
        if all_steps_succeeded:
            self.logger.console.print("\n[bold green]✅ Entire test plan completed successfully.[/bold green]")
        else:
            self.logger.console.print("\n[bold red]❌ Test plan finished with one or more failed steps.[/bold red]")
            
        return workflow_state