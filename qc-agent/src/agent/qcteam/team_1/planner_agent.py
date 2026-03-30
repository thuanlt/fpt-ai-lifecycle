import config
from agent.agent import AbstractAgent
from models.model_info import ModelInfo
from memory.shared_memory import SharedMemory

class PlannerAgent(AbstractAgent):
    def __init__(self, agent_profile: dict, model_info: ModelInfo = None, mcp_clients: list = None, shared_memory: SharedMemory = None, logger=None):
        # Cấu hình model mặc định cho Planner nếu không được truyền vào
        if not model_info:
            model_info = ModelInfo(
                model_name=getattr(config, 'LLM_MODEL_NAME', 'Qwen3-32B'),
                api_key=getattr(config, 'FPT_API_KEY', ''),
                base_url=getattr(config, 'FPT_API_BASE', '')
            )
        super().__init__(agent_profile, model_info, mcp_clients, shared_memory, logger)

    def agent_as_a_function_description(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.profile['name'],
                "description": "Select the planner agent to determine the next step in the test plan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_test_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string", "description": "Unique identifier for the test step."},
                                    "description": {"type": "string", "description": "Detailed description of the test step."},
                                    "expected_result": {"type": "string", "description": "Expected outcome of the test step."}
                                },
                                "required": ["step_id", "description", "expected_result"]
                            },
                            "description": "The complete list of test steps to be executed."
                        },
                        "current_state": {
                            "type": "object",
                            "description": "The current state of the system, including completed steps and any relevant context.",
                            "properties": {
                                "completed_steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of step_ids that have been completed."
                                },
                                "other_context": {
                                    "type": "object",
                                    "description": "Any additional context relevant to determining the next step."
                                }
                            },
                            "required": ["completed_steps"]
                        }
                    },
                    "required": ["next_step"]
                }
            }
        }

    async def run(self, step_index: int, full_test_plan: list[dict], current_state: dict) -> dict:
        self.logger.console_log(step_index, self.profile['name'], "Determining next step...")
        
        response_obj, json_str = None, None
        task_description = f"""
**Full Test Plan:**
{json.dumps(full_test_plan, indent=2)}

**Current System State:**
{json.dumps(current_state, indent=2)}

**Instructions:**
The following steps are completed: {current_state.get('completed_steps', [])}. 
Identify the next uncompleted step and formulate the action for it.
"""
        
        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        response_obj = await self._execute_llm_call(system_prompt, task_description)

        if response_obj:
            llm_message = response_obj.choices[0].message
            json_str = llm_message.content
            json_str = json_str[json_str.find('{'):json_str.rfind('}')+1].replace("''", '""')

            self.memory.shared_memory.write_to_shared_log(
                agent_id=self.profile.get("name"),
                message=json_str
            )
        
        self.logger.log_agent_step(
            step_index=step_index,
            agent_name=self.profile['name'],
            system_prompt=system_prompt,
            user_prompt=task_description,
            llm_response=response_obj.choices[0].message if response_obj else "LLM call failed."
        )
        
        try:
            rs = json.loads(json_str)
            self.logger.console_log(step_index, self.profile['name'], f"Planner Agent Response: \n{json.dumps(rs, indent=2)}")
            return rs
        except (json.JSONDecodeError, IndexError, TypeError):
            self.logger.console.print(f"[bold red]Planner Agent: Failed to decode JSON from LLM response.[/bold red]")
            return {"error": "Invalid JSON response from planner LLM."}