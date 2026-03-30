# ./agent/qcteam/verifier_agent.py
import json
from agent import AbstractAgent
from memory.shared_memory import SharedMemory

class VerifierAgent(AbstractAgent):
    def __init__(self, agent_profile: dict, mcp_clients: list = None, shared_memory: SharedMemory = None, logger=None):
        super().__init__(agent_profile, mcp_clients, shared_memory, logger)

    def agent_as_a_function_description(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.profile['name'],
                "description": "Verify the result of a QC task execution against the expected result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "execution_result": {
                            "type": "object",
                            "description": "The actual result obtained from executing the QC task."
                        },
                        "expected_result": {
                            "type": "string",
                            "description": "A detailed description of the expected outcome for the QC task."
                        }
                    },
                    "required": ["execution_result", "expected_result"]
                }
            }
        }

    async def run(self, step_index: int, execution_result: dict, expected_result: str) -> dict:
        self.logger.console_log(step_index, self.profile['name'], "Verifying execution result...")
        
        response_obj, json_str = None, None
        task_description = f"""
**Expected Result Description:**
{expected_result}

**Actual Execution Result:**
{json.dumps(execution_result, indent=2)}

**Instructions:**
Compare the actual result with the expected result.
"""
        
        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        response_obj = await self._execute_llm_call(system_prompt, task_description)

        if response_obj:
            llm_message = response_obj.choices[0].message
            json_str = llm_message.content
            json_str = json_str[json_str.find('{'):json_str.rfind('}')+1].replace("''", '""')

            self.memory.shared_memory.write_to_shared_log(
                agent_id=self.profile.get("name"),
                message=json_str)

        self.logger.log_agent_step(
            step_index=step_index,
            agent_name=self.profile['name'],
            system_prompt=system_prompt,
            user_prompt=task_description,
            llm_response=response_obj.choices[0].message if response_obj else "LLM call failed."
        )
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError, TypeError):
            self.logger.console.print(f"[bold red]Verifier Agent: Failed to decode JSON from LLM response.[/bold red]")
            return {"status": "FAILURE", "reason": "Could not parse verifier LLM response."}