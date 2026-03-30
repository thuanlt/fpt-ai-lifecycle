# src/agent/qcteam/team_3/verifier_agent.py
import json
from agent import AbstractAgent

class VerifierAgent(AbstractAgent):
    """
    Analyzes the current state of a high-level task step, its goal, and the history
    of actions taken so far. It determines if the step is DONE, needs to be SKIPPED,
    has FAILED, or is INPROGRESS, and suggests the next micro-action if applicable.
    """
    def __init__(self, agent_profile: dict, logger=None, shared_memory=None):
        super().__init__(agent_profile, logger=logger, shared_memory=shared_memory)

    def agent_as_a_function_description(self) -> dict:
        # This agent is called internally by the orchestrator, not as a tool.
        return {}

    async def run(self, step_index: int, current_step_goal: dict, execution_history: list, retry_count: int) -> dict:
        self.logger.console_log(step_index, self.profile['name'], "Analyzing current step state...")

        task_description = f"""
**Current High-Level Goal:**
- **Name:** {current_step_goal.get('name')}
- **Description:** {current_step_goal.get('description')}
- **Expected Result:** {current_step_goal.get('expected_result')}

**Execution History for this Goal (most recent last):**
{json.dumps(execution_history, indent=2) if execution_history else "No actions have been taken for this goal yet."}

**Retry Count:** {retry_count}

**Your Task:**
Based on the goal and the history, evaluate the current status and decide the next action. Your response MUST be a single JSON object with the following structure:
- "status": Choose one of [DONE, SKIP, FAILED, INPROGRESS].
  - "DONE": The goal has been successfully achieved.
  - "SKIP": The goal's expected result is already met by the current system state, so no action is needed.
  - "FAILED": The goal cannot be achieved (e.g., max retries exceeded, unrecoverable error). You must carefully analyze current state and history to justify this. Once marked as FAILED, the orchestrator will stop further attempts on this goal.
  - "INPROGRESS": The goal is not yet achieved and requires more actions.
- "analysis": A brief, clear analysis of the current situation.
- "next_action": If the status is "INPROGRESS" or "FAILED", provide a clear, specific, and actionable description of the *next small step* to take. This description will be given to an Executor Agent. If status is not "INPROGRESS", this can be an empty string.
"""

        verifier_response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "Plan",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "analysis": {"type": "string"},
                        "next_action": {"type": "string"}
                    },
                    "required": ["testing_plan", "post_testing_plan"]
                },
                "strict": True # Ensures strict adherence to the schema
            }
        }

        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        llm_response = await self._execute_llm_call(system_prompt, task_description, response_format=verifier_response_format, need_parse=False)

        try:
            verification_result = json.loads(llm_response)

            self.logger.console_log(
                step_index,
                self.profile['name'],
                f"Verification Result: Status - {verification_result.get('status')}, Analysis - {verification_result.get('analysis')}"
            )
            self.memory.shared_memory.write_to_shared_log(
                self.profile['name'],
                f"Verification: {json.dumps(verification_result)}"
            )
            return verification_result

        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            self.logger.console.print(f"[bold red]Verifier Agent Error: Could not parse LLM response. Error: {e}[/bold red]")
            return {
                "status": "FAILED",
                "analysis": "Internal error: Verifier LLM returned an invalid response.",
                "next_action": ""
            }