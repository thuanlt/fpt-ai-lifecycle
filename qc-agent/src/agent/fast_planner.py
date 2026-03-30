import json
import config
from agent.agent import AbstractAgent
from models.model_info import ModelInfo
from memory.shared_memory import SharedMemory
from prompt.prompt_builder import builder
from utils.logger import Logger
import os

class FastPlannerAgent(AbstractAgent):
    def __init__(self, model_info: ModelInfo = None, shared_memory: SharedMemory = None, mcp_clients: list = None, memory=None):
        logger = Logger()
        
        if not model_info:
            model_info = ModelInfo(model_name=getattr(config, 'FAST_PLANNER_MODEL', 'SaoLa-Llama3.1-planner'))
        super().__init__(
            agent_profile=builder.load_agent_profile("fast_planner_agent"),
            model_info=model_info,
            mcp_clients=mcp_clients,
            logger=logger,
            shared_memory=shared_memory
        )
        self.memory = memory or self.memory

    def agent_as_a_function_description(self) -> dict:
        return {}
        
    async def run(self, user_instruction: str, metadata: dict) -> dict:
        print(f"\n[DEBUG-PLANNER] --- Starting Planner Agent ---")
        self.logger.console_log(0, self.profile['name'], f"Received Fast Track Task: {user_instruction}")
        
        prompt_rules = ""
        prompt_path = os.path.join(getattr(config, 'WORKING_DIR', os.getcwd()), "docs", "prompt_tester.md")
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_rules = f.read()
            except: pass

        # 2. Truy vấn từ Bộ nhớ dài hạn (Vector DB)
        related_memories = []
        if self.memory and self.memory.ltm:
            try:
                related_memories = self.memory.ltm.retrieve(
                    query=user_instruction,
                    top_k_broad=10,
                    top_k_final=5
                )
                print(f"[DEBUG-PLANNER] MEMORY: Found {len(related_memories)} related items.")
            except Exception as e:
                print(f"WARNING: Memory retrieval error: {e}")

        ltm_context = "\n".join([f"- {m}" for m in related_memories]) if related_memories else "No related history found."

        task_description = f"""
**User Instruction / SRS Document / Link:**
{user_instruction}

**Universal Metadata:**
{json.dumps(metadata, indent=2)}

**Test Engineering Rules (The Standard):**
{prompt_rules}

**Long-term Memory Context:**
{ltm_context}

**Your Objective:**
Plan the testing tasks. If the 'User Instruction' contains a link, USE your available tools (like `browser_navigate`, `browser_get_content` or `browser_screenshot`) to visit the link and read the document content FIRST before producing the final plan.

**Categorization Strategy:**
You MUST divide the testing work into logical BatchTasks focus on: UI/UX, Validation, Func, API.
- **IMPORTANT**: ALWAYS create NEW tasks for everything. DO NOT try to map with any existing Jira IDs even if they look similar. 

**Task Assignment Rules:**
- Set `tester` to "Senior SDET" (formerly Senior Tester).
- Set `target` to the component name.
- Set `jira_test_case_id` to EMPTY STRING "" for ALL tasks (Disable Mapping).
- The `description` MUST be detailed and EXPLICITLY ask the SDET to produce both the Markdown Test Script and the Playwright Python Automation Code.

**Output Requirements:**
Once you have all information, output a final JSON following this schema:
{{
    "plan_overview": "A high-level summary of the testing strategy...",
    "tasks": [
        {{
            "id": "task_1",
            "tester": "Senior SDET",
            "description": "Create test script and automation code for login feature...",
            "target": "Login Component",
            "jira_test_case_id": ""
        }}
    ],
    "metadata_context": {{}}
}}
"""
        # Cố định schema đầu ra cho Planner
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "BatchTask",
                "schema": {
                    "type": "object",
                    "properties": {
                        "plan_overview": {"type": "string"},
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "tester": {"type": "string"},
                                    "description": {"type": "string"},
                                    "target": {"type": "string"},
                                    "jira_test_case_id": {"type": "string"}
                                },
                                "required": ["id", "tester", "description", "target"]
                            }
                        },
                        "metadata_context": {"type": "object"}
                    },
                    "required": ["plan_overview", "tasks", "metadata_context"]
                }
            }
        }
        
        system_prompt = builder.build_system_prompt("fast_planner_agent", {})

        # Thực thi LLM với vòng lặp Tool-calling (Centralized in AbstractAgent)
        response_result = await self.run_with_tools(
            system_prompt,
            task_description,
            max_steps=5
        )
        
        if not response_result:
            return None
            
        # Xử lý kết quả cuối cùng
        try:
            content = self.cut_thinking_step(response_result.content)
            json_str = self._clean_json_string(content)
            batch_task = json.loads(json_str)
            
            if self.memory and self.memory.shared_memory:
                self.memory.shared_memory.write_to_shared_log(self.profile['name'], f"Planned {len(batch_task.get('tasks', []))} tasks.")
            
            # --- DEBUG FINAL OUTPUT ---
            print(f"\n[DEBUG-FINAL-OUTPUT] Planner Result: {json.dumps(batch_task, indent=2)}")
            return batch_task
        except Exception as e:
            # Nếu parsing thất bại, thử gọi LLM một lần nữa với response_format để ép JSON
            print(f"[DEBUG-PLANNER] ERROR: JSON Parse Error: {e}, retrying with response_format...")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Previous response was not valid JSON. Please provide the final BatchTask JSON now based on: {response_result.content}"}
            ]
            final_llm_response = await self._execute_llm_call(
                messages=messages,
                response_format=response_format
            )
            if final_llm_response:
                try:
                    content = self.cut_thinking_step(final_llm_response.choices[0].message.content)
                    json_str = self._clean_json_string(content)
                    batch_task = json.loads(json_str)
                    return batch_task
                except: pass
            return None
