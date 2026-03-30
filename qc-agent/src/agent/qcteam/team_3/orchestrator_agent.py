# src/agent/qcteam/team_3/orchestrator_agent.py
import asyncio
import json
import config
from time import time
from agent import AbstractAgent
from .verifier_agent import VerifierAgent
from .executor_agent import ExecutorAgent
from memory.shared_memory import SharedMemory
from utils.logger import Logger
from prompt.prompt_builder import builder
from contextlib import AsyncExitStack
from pydantic import BaseModel
from typing import List, Dict, Any


class StepPlan(BaseModel):
    name: str
    description: str
    expected_result: str

class Plan(BaseModel):
    testing_plan: List[StepPlan]
    post_testing_plan: List[StepPlan]

class OrchestratorAgent(AbstractAgent):
    """
    The master agent for team_3. It performs two main phases:
    1.  Planning: Generates a high-level plan based on the initial test case.
    2.  Execution: Iterates through the plan, using a Verifier-Executor loop
        to complete each step.
    """
    def __init__(self):
        logger = Logger()
        shared_memory = SharedMemory()
        
        super().__init__(
            agent_profile=builder.load_agent_profile("orchestrator_agent"),
            logger=logger,
            shared_memory=shared_memory
        )
        self.shared_memory = shared_memory

        self.verifier = VerifierAgent(
            agent_profile=builder.load_agent_profile("verifier_agent"),
            logger=self.logger,
            shared_memory=self.shared_memory
        )
        self.executor = ExecutorAgent(
            agent_profile=builder.load_agent_profile("executor_agent"),
            logger=self.logger,
            shared_memory=self.shared_memory
        )

    def agent_as_a_function_description(self) -> dict:
        return {}

    # <-- CHANGED: Renamed and updated to generate two distinct plans
    async def _generate_plans(self, test_case_steps: list[dict]) -> tuple[list[dict], list[dict]]:
        """Phase 1: Generate two distinct high-level execution plans."""
        self.logger.console_log(0, self.profile['name'], "Generating testing and post-testing plans...")

        output_timestamp_postfix = int(time())

        task_description = f"""
**Input Test Case Steps:**
{json.dumps(test_case_steps, indent=2)}

**Your Task:**
Create a single JSON object containing two plans: "testing_plan" and "post_testing_plan".

1.  **"testing_plan"**: Convert ONLY the "Input Test Case Steps" into a detailed, step-by-step execution plan, your description for each step should be clear and actionable, and MUST include all information from user-provided steps beside your additional details.
2.  **"post_testing_plan"**: Create a plan for the mandatory tasks that must run AFTER the testing is complete. This plan should include:
    a. Write test sumarization and final result follow below steps, using ONLY file operation tool:
        - List all files in "{config.WORKING_DIR}/tmp/template"
        - Choose ONLY ONE appropriated template file in template folder for test report
        - Read the CHOOSED TEMPLATE file to get template content, NOTE that you must use absolute path to read file to avoid error
        - Write test sumarization to file "{config.WORKING_DIR}/tmp/Result_{output_timestamp_postfix}.txt" using the template.
    b. Write playwright automation script in typescript to file "{config.WORKING_DIR}/tmp/automation_{output_timestamp_postfix}.ts" 
    c. Capture screenshot of the final state. Then copy the generated file to "{config.WORKING_DIR}/tmp/screenshot_{output_timestamp_postfix}.png"
Each step in both plans must be a JSON object with these keys:
- "name": A short, descriptive name for the step.
- "description": A detailed, clear description of what needs to be done.
- "expected_result": The specific, verifiable outcome for the step.

Your final output must be a single JSON object like this:
{{
  "testing_plan": [{{...}}, {{...}}],
  "post_testing_plan": [{{...}}, {{...}}]
}}
"""
        plan_response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "Plan",
                "schema": {
                    "type": "object",
                    "properties": {
                        "testing_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "expected_result": {"type": "string"}
                                },
                                "required": ["name", "description", "expected_result"]
                            }
                        },
                        "post_testing_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "expected_result": {"type": "string"}
                                },
                                "required": ["name", "description", "expected_result"]
                            }
                        }
                    },
                    "required": ["testing_plan", "post_testing_plan"]
                },
                "strict": True # Ensures strict adherence to the schema
            }
        }

        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        llm_response = await self._execute_llm_call(system_prompt, task_description, response_format=plan_response_format, need_parse=False)

        try:
            plans = json.loads(llm_response)
            testing_plan = plans.get("testing_plan", [])
            post_testing_plan = plans.get("post_testing_plan", [])
            
            self.logger.console_log(0, self.profile['name'], f"Generated Testing Plan:\n{json.dumps(testing_plan, indent=2)}")
            self.logger.console_log(0, self.profile['name'], f"Generated Post-Testing Plan:\n{json.dumps(post_testing_plan, indent=2)}")
            
            return testing_plan, post_testing_plan
        except (json.JSONDecodeError, AttributeError, IndexError, KeyError) as e:
            self.logger.console.print(f"[bold red]Orchestrator Error: Failed to generate or parse plans. Error: {e}[/bold red]")
            return None, None

    # <-- NEW: Helper method to execute a given plan and return its success status
    async def _execute_plan_steps(self, plan: list[dict], final_results: dict, step_index_offset: int = 0, max_retries_per_step: int = 20) -> bool:
        """
        Executes a list of plan steps and returns True if all succeed, False otherwise.
        """
        all_steps_succeeded = True
        failed_retry_count = 0
        for i, step_goal in enumerate(plan):
            step_index = i + 1 + step_index_offset
            self.logger.console.print(f"\n" + "="*20 + f" EXECUTING PLAN STEP {step_index}: {step_goal['name']} " + "="*20)

            execution_history = []
            step_status = "INPROGRESS"
            failed_retry_count = 0

            for attempt in range(max_retries_per_step):
                failed_retry_count += 1
                verification = await self.verifier.run(
                    step_index=step_index,
                    current_step_goal=step_goal,
                    execution_history=execution_history,
                    retry_count=attempt
                )
                step_status = verification.get("status", "FAILED")

                if step_status in ["DONE", "SKIP"]:
                    break

                if step_status == "FAILED" and failed_retry_count >= 5:
                    self.logger.console.print(f"[bold red]Step {step_index} failed: Max retries ({max_retries_per_step}) reached.[/bold red]")
                    break
                
                next_action = verification.get("next_action")
                if not next_action:
                    step_status = "FAILED"
                    self.logger.console.print(f"[bold red]Step {step_index} failed: Verifier returned FAILED.[/bold red]")
                    break
                
                execution_result = await self.executor.run(
                    step_index=step_index,
                    analysis=verification.get("analysis", ""),
                    next_action=next_action
                )
                execution_history += execution_result
                # execution_history.append(execution_result)

                # if execution_result.get("status") == "error":
                #     step_status = "FAILED"
                #     break
            
            if attempt == max_retries_per_step - 1 and step_status == "INPROGRESS":
                self.logger.console.print(f"[bold red]Step {step_index} failed: Max retries ({max_retries_per_step}) reached.[/bold red]")
                step_status = "FAILED"

            final_results["step_results"].append({
                "step_name": step_goal['name'],
                "status": step_status,
                "history": execution_history
            })
            self.logger.console.print(f"--- Step {step_index} Final Status: {step_status} ---")

            if step_status == "FAILED":
                all_steps_succeeded = False
                break # Stop executing this particular plan
        
        return all_steps_succeeded

    async def run(self, test_case_steps: list[dict], max_retries_per_step: int = 20):
        """Main entry point to run the entire two-phase workflow."""
        self.logger.console_log(0, self.profile['name'], "Starting Team 3 Workflow...")

        try:
            testing_plan, post_testing_plan = await self._generate_plans(test_case_steps)
        except Exception as e:
            print(f"Orchestraror error {e}")
        
        if testing_plan is None or post_testing_plan is None:
            self.logger.console.print("[bold red]Aborting workflow due to planning failure.[/bold red]")
            return

        final_results = {"overall_status": "IN_PROGRESS", "step_results": []}
        
        mcp_plugins = []
        try:
            # BƯỚC 2: GỌI KHỞI TẠO TOOLS CHO QC_AGENT (THAY ĐỔI MỚI)
            mcp_plugins += await self.executor.initialize_delegated_tools()

            # --- PHASE 1: EXECUTE TESTING PLAN ---
            self.logger.console.print("\n" + "#"*20 + " STARTING TESTING PHASE " + "#"*20)
            testing_successful = await self._execute_plan_steps(
                testing_plan, final_results, max_retries_per_step=max_retries_per_step
            )

            # --- PHASE 2: EXECUTE POST-TESTING PLAN (ALWAYS RUNS) ---
            self.logger.console.print("\n" + "#"*20 + " STARTING POST-TESTING PHASE " + "#"*20)
            # The logic for whether to generate the script is now embedded in the plan's description,
            # which the Verifier/Executor agents will handle.
            await self._execute_plan_steps(
                post_testing_plan, final_results, step_index_offset=len(testing_plan), max_retries_per_step=max_retries_per_step
            )
        except Exception as e:
            print(f"Orchestraror error {e}")
        finally:
            for client in reversed(mcp_plugins):
                await client.__aexit__(None, None, None)

        final_results["overall_status"] = "SUCCESS" if testing_successful else "FAILED"
        
        print("\n" + "="*20 + " WORKFLOW FINISHED " + "="*20)
        # print(json.dumps(final_results, indent=2))
        return final_results