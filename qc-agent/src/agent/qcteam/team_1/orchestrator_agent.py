# orchestrator_agent.py
import asyncio
import json
import config
from prompt.prompt_builder import builder
from memory import MemoryManager
from tools.mcpclient import MCPClient

from memory.shared_memory import SharedMemory
from contextlib import AsyncExitStack

from ...agent import AbstractAgent
from .planner_agent import PlannerAgent
from .qc_agent import QCAgent
from .verifier_agent import VerifierAgent
from utils.logger import Logger

shared_memory = SharedMemory()

class OrchestratorAgent(AbstractAgent):
    def __init__(self):
        logger = Logger()  # Create a single logger for the entire workflow session

        super().__init__(
            agent_profile=builder.load_agent_profile("orchestrator_agent"),
            mcp_clients=None,
            shared_memory=shared_memory,
            logger=logger  # Pass logger to self
        )

        # Initialize child agents, sharing the same logger instance
        self.planner = PlannerAgent(
            agent_profile=builder.load_agent_profile("planner_agent"),
            mcp_clients=None,
            shared_memory=shared_memory,
            logger=logger
        )

        self.qc_mcp_clients = []
        if config.MCP_SERVERS_CONFIG:
            for server_name, server_config in config.MCP_SERVERS_CONFIG.items():
                print(f"Initializing MCP client for '{server_name}'...")
                self.qc_mcp_clients.append(MCPClient(server_config))
        
        self.qc_agent = QCAgent(
            agent_profile=builder.load_agent_profile("qc_agent"),
            mcp_clients=self.qc_mcp_clients,
            shared_memory=shared_memory,
            logger=logger
        )
        
        self.verifier = VerifierAgent(
            agent_profile=builder.load_agent_profile("verifier_agent"),
            mcp_clients=None,
            shared_memory=shared_memory,
            logger=logger
        )
        
        self.agents = {
            "PlannerAgent": self.planner,
            "QCAgent": self.qc_agent,
            "VerifierAgent": self.verifier,
        }

        # In OrchestratorAgent, create this tool definition
        self.delegation_tool = [
            # self.planner.agent_as_a_function_description(),
            self.qc_agent.agent_as_a_function_description(),
            # self.verifier.agent_as_a_function_description(),
            {
                "type": "function",
                "function": {
                    "name": "Finish",
                    "description": "Call when the the testing processing is done.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "string",
                                "description": "Must be PASS or FAILED"
                            }
                        },
                        "required": ["result"]
                    }
                }
            }
        ]

        # Add delegation tool to the agent's tools
        self.tools = self.delegation_tool

    async def run(self, test_plan_: list[dict]):
        print("\n\n" + "="*20 + " STARTING LLM-DRIVEN TEST PLAN EXECUTION " + "="*20)

        # response = self.llm_client.chat.completions.create(
        #     model=config.LLM_MODEL_NAME,
        #     messages=[
        #         {"role": "user", "content": f"Convert to Markdown format in a clear and detail style, do not use table style, easy for LLM exploit information, you only return converted doc without any additional information: {json.dumps(test_plan_, indent=2)}"}
        #     ],
        #     temperature=0.0,
        # )
        # test_plan_md = self.cut_thinking_step(response.choices[0].message.content)
        # self.logger.console_log(0, self.profile['name'], f"Generated Test Plan Markdown:\n {test_plan_md}")

        state = {
            "full_test_plan": f"{json.dumps(test_plan_, indent=2)}",
            "completed_steps": [],
            "last_action_result": None,
            "system_data": {}
        }
        
        async with AsyncExitStack() as stack:
            await asyncio.gather(*[stack.enter_async_context(client) for client in self.qc_mcp_clients])

            # BƯỚC 2: GỌI KHỞI TẠO TOOLS CHO QC_AGENT (THAY ĐỔI MỚI)
            await self.qc_agent.initialize_tools()

            turn = 1
            while turn <= 100: # Safety break
                try:
                    self.logger.console_log(turn, self.profile['name'], "Deciding next action...")
                    
                    # 1. ORCHESTRATOR: Make a decision
#                     task_description = f"""
# **Full Test Plan:**
# {json.dumps(state['full_test_plan'], indent=2)}

# **Instruction:**
# Based on the Current System State, decide one agent should run next and what its input should be.
# - If the plan is not started or a step just finished successfully, call PlannerAgent.
# - If the planner has just returned an action, call QCAgent.
# - If the QC agent has just returned a result, call VerifierAgent.
# - If all steps are completed, call 'Finish'.

# **Current System State:**
# {json.dumps({k: v for k, v in state.items() if k != 'full_test_plan'}, indent=2)}

# YOU ONLY SELECT ONE TOOL AT A TIME
# THE PROCESS WILL CRASH IF YOU SELECT MULTIPLE TOOLS
# """
#                     task_description = f"""
# **Full Test Plan:**
# {json.dumps(state['full_test_plan'], indent=2)}

# **Instruction:**
# Based on the Current System State, decide one agent should run next and what its input should be.
# - Call QCAgent to do test action.
# - Call VerifierAgent to verify current state.
# - If all steps are completed, write test sumarization and final result to file "/Users/huepro/tmp/Result.txt"
# - Finally, call "Finish"

# **Current System State:**
# {json.dumps({k: v for k, v in state.items() if k != 'full_test_plan'}, indent=2)}

# YOU ONLY SELECT ONE TOOL AT A TIME
# THE PROCESS WILL CRASH IF YOU SELECT MULTIPLE TOOLS
# """ # Work well with GLM
                    
                    task_description = f"""
**Full Test Plan:**
{json.dumps(state['full_test_plan'], indent=2)}

**Instruction:**
Based on the Current System State, decide one agent should run next and what its input should be.
1. Call QCAgent to do test action.
    - Analyze that if a on going step in test plan have already matched expectation, you can skip it
    - If a step is FAILED to execute, retry 5 more times.
2. Call VerifierAgent to verify current state after calling QCAgent action.
3. If all steps are completed, write test sumarization and final result to file "/Users/huepro/tmp/Result.txt"
4. Finally, call "Finish"

**Current System State:**
{json.dumps({k: v for k, v in state.items() if k != 'full_test_plan'}, indent=2)}

YOU ONLY SELECT ONE TOOL AT A TIME. IF YOU PROVIDE MORE THAN 1 TOOL, I WILL CHOOSE THE FIRST ONE, AND IGNORE OTHERS.
"""
                        
                    system_prompt = self.memory.assemble_prompt(self.profile, task_description)
                    decision_response = await self._execute_llm_call(system_prompt, task_description, use_tool=True, tool_choice='required')
                    # print(decision_response)
                    if not decision_response:
                        self.logger.console.print("[bold red]Orchestrator failed to get a decision from LLM. Aborting.[/bold red]")
                        break

                    self.logger.log_agent_step(
                        step_index=turn,
                        agent_name=self.profile['name'],
                        system_prompt=system_prompt,
                        user_prompt=task_description,
                        llm_response=decision_response.choices[0].message
                    )
                    try:
                        # json_str = decision_response.choices[0].message.content
                        # json_str = json_str[json_str.find('{'):json_str.rfind('}')+1].replace("''", '""')
                        # decision_json = json.loads(json_str)                    
                        
                        tool_call = decision_response.choices[0].message.tool_calls[0]
                        json_arguments_string = tool_call.function.arguments 
                        next_agent_name = tool_call.function.name

                        task_input = json.loads(json_arguments_string)
                        self.memory.shared_memory.write_to_shared_log(
                            agent_id=self.profile.get("name"),
                            message=f"Decision: Next agent is '{next_agent_name}'\nInput: {json.dumps(task_input, indent=2)}"
                        )
                        # task_input = decision_json.get("task_input", {})
                        self.logger.console_log(turn, self.profile['name'], f"Decision: Next agent is '{next_agent_name}'\nInput: {json.dumps(task_input, indent=2)}")
                    except Exception as e:
                        self.logger.console_log(turn, self.profile['name'], f"[bold red]❌ Orchestrator failed to parse its own decision: {e}. Aborting.[/bold red]")
                        break
                    
                    # 2. Execute decision
                    if next_agent_name == "Finish":
                        self.logger.console_log(turn, self.profile['name'], f"✅ All steps completed. Finishing execution. {task_input}")
                        break
                    
                    agent_to_run = self.agents.get(next_agent_name)
                    if not agent_to_run:
                        self.logger.console.print(f"[bold red]❌ Unknown agent '{next_agent_name}'. Aborting.[/bold red]")
                        break
                    
                    # Call the sub-agent, passing the turn index
                    result = await agent_to_run.run(step_index=turn, **task_input)
                    
                    # 3. Update state
                    state["last_action_result"] = result
                    state["completed_steps"].append(f"Step {turn}, orchestrator call {next_agent_name}")
                    
                    # (Intelligent state update logic can be added here)

                    turn += 1

                except Exception as e:
                    self.logger.console.print(f"[bold red]❌ An error occurred during orchestration: {e}[/bold red]")
                    break
                
                if turn > 20:
                    self.logger.console.print("[bold red]❌ Reached turn limit. Aborting.[/bold red]")

        print("\n" + "="*20 + " TEST PLAN EXECUTION FINISHED " + "="*20)
    
    def agent_as_a_function_description(self) -> dict:
        return {}