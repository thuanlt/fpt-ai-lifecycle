# ./agent/singletester/single_qc_1.py
import json
import asyncio
from agent import AbstractAgent
from memory.shared_memory import SharedMemory
from tools.mcpclient import MCPClient
from utils.logger import Logger
import config

from contextlib import AsyncExitStack

# Define the agent's profile directly in the file for encapsulation.
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


class SingleQCAgent(AbstractAgent):
    """
    An autonomous agent that handles the entire test execution workflow:
    planning, executing actions via MCP, and verifying results for each step.
    It is designed to handle complex steps that may require multiple actions.
    """

    def __init__(self, mcp_clients: MCPClient = None, shared_memory: SharedMemory = None, logger: Logger = None):
        """
        Initializes the SingleQCAgent.

        Args:
            mcp_client: An initialized MCPClient for tool execution.
            shared_memory: The shared memory instance for inter-agent communication (if any).
            logger: The logger instance for logging workflow steps.
        """
        # The agent's profile is sourced from the constant defined above.
        _mcp_clients = [
            MCPClient(config.MCP_TOOLS[tool_name]["url"]) for tool_name in config.MCP_TOOLS.keys()
        ] if config.MCP_TOOLS else []

        _logger = Logger()

        super().__init__(SINGLE_QC_AGENT_PROFILE, mcp_clients=_mcp_clients, shared_memory=None, logger=_logger)

    def agent_as_a_function_description(self) -> dict:
        """This agent is a top-level executor and is not designed to be a callable tool."""
        return {}

    async def run(self, test_plan: list[dict], max_step_attempts: int = 100) -> dict:
        """
        Executes the entire test plan from start to finish.

        Args:
            test_plan (list[dict]): A list of test steps, where each step is a dictionary
                                    with 'id', 'description', and 'expectedResult'.
            max_step_attempts (int): The maximum number of attempts per test step.

        Returns:
            dict: A final report of the test execution, including the status of each step.
        """
        self.logger.console_log(0, self.profile['name'], "Starting autonomous test execution workflow.")

        workflow_state = {
            "test_plan_name": "Unnamed Test Plan", # This could be an input parameter
            "overall_status": "In Progress",
            "completed_steps": [],
            "step_results": {},
        }

        async with AsyncExitStack() as stack:
            try:
                await asyncio.gather(*[stack.enter_async_context(client) for client in self.mcp_clients])

                for step_index, step in enumerate(test_plan):
                    print(json.dumps(step, indent=2))
                    step_id = step.get('id') or f"step_{step_index + 1}"
                    self.logger.console_log(step_index + 1, self.profile['name'], f"--- Starting Step: {step_id} ---")
                    
                    step_completed_successfully = False
                    last_execution_result = []
                    
                    for attempt in range(1, max_step_attempts + 1):
                        self.logger.console_log(step_index + 1, self.profile['name'], f"Attempt {attempt}/{max_step_attempts} for step {step_id}")

                        # Tool run step
                        task_description = f"""**Full Test Plan is**
{json.dumps(test_plan)}
**Current Goal (Step {step_id})**: {step['description']}
**Expected Final Outcome**: {step['expectedResult']}

**History of this Step's Last Action**:
{json.dumps(last_execution_result, indent=2)}

**Your Task**:
1.  Analyze the **Current Goal** and the **History**.
2.  If the goal is not met, choose **one tool** that will make progress towards the goal.
"""

                        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
                        llm_response = await self._execute_llm_call(system_prompt, task_description, use_tool=True, tool_choice='auto')

                        if not llm_response:
                            last_execution_result = "LLM call failed. Retrying."
                            continue

                        response_message = llm_response.choices[0].message
                        
                        if response_message.tool_calls:
                            tool_call = response_message.tool_calls[0]
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            self.logger.console_log(step_index + 1, "ToolCall", f"Executing: {tool_name}({json.dumps(tool_args)})")
                            execution_result = await self.execute_tool(tool_name, tool_args)
                            last_execution_result.append(execution_result)

                            # execution_result = await self.execute_tool(tool_name, tool_args)
                            # last_execution_result.append(execution_result)

                        task_description = f"""**Full Test Plan is**
{json.dumps(test_plan)}
**Current Goal (Step {step_id})**: {step['description']}
**Expected Final Outcome**: {step['expectedResult']}

**History of this Step's Last Action**:
{json.dumps(last_execution_result, indent=2)}

**Your Task**:
1.  Analyze the **Current Goal** and the **History**.
2.  If the **History** shows the goal is fully met, output a final JSON:
    `{{"status": "SUCCESS", "reason": "Explain why the step is now complete."}}`
3.  If the step is impossible to complete or has unrecoverably failed, output a final JSON:
    `{{"status": "FAILURE", "reason": "Explain the cause of the failure."}}`
4. If the step is possible to complete, output a final JSON:
    `{{"status": "NOT_DONE", "reason": "Explain the next step."}}`
5. If the step does not need to do next step in test plan, and you does not need to do it and output:
    `{{"status": "DONE", "reason": "Explain the next step."}}`
"""
                        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
                        llm_response = await self._execute_llm_call(system_prompt, task_description)

                        try:
                            json_content = self.cut_thinking_step(llm_response.choices[0].message.content)
                            json_content = json_content[json_content.find('{'):json_content.rfind('}') + 1]
                            final_verdict = json.loads(json_content)
                            
                            self.logger.console_log(step_index + 1, "Verify", f"Executing: {json.dumps(final_verdict, indent=2)}")
                            
                            if final_verdict.get("status") == "SUCCESS":
                                self.logger.console.print(f"[bold green]✅ Step {step_id} VERIFIED as SUCCESS.[/bold green]")
                                workflow_state["step_results"][step_id] = {
                                    "status": "SUCCESS",
                                    "reason": final_verdict.get("reason", "No reason provided."),
                                    "attempts": attempt,
                                }
                                step_completed_successfully = True
                            elif final_verdict.get("status") == "DONE":
                                self.logger.console.print(f"[bold green]✅ Step {step_id} VERIFIED as SUCCESS.[/bold green]")
                                workflow_state["step_results"][step_id] = {
                                    "status": "SUCCESS",
                                    "reason": final_verdict.get("reason", "No reason provided."),
                                    "attempts": attempt,
                                }
                                step_completed_successfully = True
                            elif final_verdict.get("status") == "FAILURE":
                                self.logger.console.print(f"[bold red]❌ Step {step_id} VERIFIED as FAILURE.[/bold red]")
                                workflow_state["step_results"][step_id] = {
                                    "status": "FAILURE",
                                    "reason": final_verdict.get("reason", "Failure reason not provided."),
                                    "attempts": attempt,
                                }
                            else:
                                self.logger.console.print(f"[bold red]❌ Step {step_id} NOT DONE YET.[/bold red]")
                                workflow_state["step_results"][step_id] = {
                                    "status": "NOT_DONE",
                                    "reason": final_verdict.get("reason", "Next step is not provided."),
                                    "attempts": attempt,
                                }

                        except (json.JSONDecodeError, TypeError):
                            error_msg = f"LLM provided a non-JSON final response: {response_message.content}"
                            self.logger.console.print(f"[bold red]Error: {error_msg}[/bold red]")
                            last_execution_result.append(error_msg)
                        
                        # Log the full step for debugging
                        self.logger.log_agent_step(
                            step_index=step_index + 1, agent_name=f"{self.profile['name']}_Attempt_{attempt}",
                            system_prompt=system_prompt, user_prompt=task_description, llm_response=response_message,
                            tool_responses=[last_execution_result[-1]] if not step_completed_successfully and len(last_execution_result) > 0 else []
                        )

                        # After the attempt loop, check the outcome
                        if step_completed_successfully:
                            workflow_state["completed_steps"].append(step_id)
                            break
                        # else:
                        #     # If loop finished due to max attempts without a SUCCESS verdict
                        #     if step_id not in workflow_state["step_results"]:
                        #         self.logger.console.print(f"[bold red]❌ Step {step_id} FAILED after {max_step_attempts} attempts.[/bold red]")
                        #         workflow_state["step_results"][step_id] = {
                        #             "status": "FAILURE",
                        #             "reason": f"Max attempts ({max_step_attempts}) reached without successful verification.",
                        #             "attempts": max_step_attempts,
                        #         }
                        #     workflow_state["overall_status"] = "Failed"
                        #     self.logger.console.print("[bold red]Workflow terminated due to step failure.[/bold red]")
                        #     return workflow_state # Terminate the entire workflow
            except Exception as e:
                error_msg = f"SingleQCAgent Error: {e}"
                self.logger.console.print(f"[bold red]Error: {error_msg}[/bold red]")

        # If all steps completed successfully
        workflow_state["overall_status"] = "Success"
        self.logger.console.print("[bold green]✅ Entire test plan completed successfully.[/bold green]")
        return workflow_state