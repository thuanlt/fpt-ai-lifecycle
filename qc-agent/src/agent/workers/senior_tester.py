import json
import config
from agent.agent import AbstractAgent
from models.model_info import ModelInfo
from memory.shared_memory import SharedMemory
from prompt.prompt_builder import builder
from utils.logger import Logger
import os

class SeniorTesterAgent(AbstractAgent):
    def __init__(self, model_info: ModelInfo = None, shared_memory: SharedMemory = None, mcp_clients: list = None):
        logger = Logger()
        # Cấu hình model mặc định cho Senior Tester nếu không được truyền vào
        if not model_info:
            model_info = ModelInfo(model_name=getattr(config, 'SENIOR_TESTER_MODEL', 'Qwen3-32B'))
        
        super().__init__(
            agent_profile=builder.load_agent_profile("senior_tester_agent"),
            model_info=model_info,
            mcp_clients=mcp_clients,
            logger=logger,
            shared_memory=shared_memory
        )

    def agent_as_a_function_description(self) -> dict:
        return {}

    async def run(self, task: dict):
        self.logger.console_log(0, self.profile['name'], f"Executing Complex Task: {task.get('description')}")
        
        prompt_rules = ""
        prompt_path = os.path.join(getattr(config, 'WORKING_DIR', os.getcwd()), "docs", "prompt_tester.md")
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_rules = f.read()
            except: pass



        # 1. Truy vấn từ Bộ nhớ dài hạn (Vector DB) dựa trên mô tả nhiệm vụ
        related_memories = []
        if self.memory and self.memory.ltm:
            try:
                related_memories = self.memory.ltm.retrieve(
                    query=task.get('description'),
                    top_k_broad=10,
                    top_k_final=5
                )
                print(f"[DEBUG-TESTER] MEMORY: Found {len(related_memories)} related items from memory.")
            except Exception as e:
                print(f"WARNING: Memory retrieval error: {e}")

        ltm_context = "\n".join([f"- {m}" for m in related_memories]) if related_memories else "No related history found."

        # System prompt được lấy từ profile của agent sử dụng builder
        system_prompt = builder.build_system_prompt("senior_tester_agent", {})

        mode = task.get("mode", "all") # "all", "generate_script", "generate_code"
        
        if mode == "generate_script":
            self.logger.console_log(0, self.profile['name'], f"Mode: SCRIPT_ONLY - Generating Forensic Script for: {task.get('target')}")
            task_description = f"""
**Task Assignment (SCRIPT ONLY):**
{json.dumps(task, indent=2)}

**Objective:**
Produce ONLY a high-quality Markdown test script (Forensic Script) for Jura based on the task description.
Do NOT generate any automation code.

**Markdown Formatting Rules:**
# [Function Name From SRS]
## [Section Name: UI/UX | Validation | Func | API]
### [Main Scenario/Group Name]
- [Jira ID or [NEW]] [Test Case Description]
    - 1. [Action]
        - => [Expected Result 1]
        - => [Expected Result 2]

**Output Requirements:**
Respond ONLY with a JSON object containing:
1. `"status"`: "PASS"
2. `"message"`: "Script generated"
3. `"evidence"`: the full markdown script.
4. `"automation_code"`: "" (Empty string)
"""
        elif mode == "generate_code":
            self.logger.console_log(0, self.profile['name'], f"Mode: CODE_GEN - Generating Playwright code for specific TC.")
            task_description = f"""
**Task Assignment (CODE GEN ONLY):**
{json.dumps(task, indent=2)}

**Input Forensic Script:**
{task.get('tc_evidence', '')}

**Objective:**
Produce ONLY the Playwright Python automation code for the specific test case described in the 'Input Forensic Script' above.

**Automation Rules:**
- Use `playwright` library in Python.
- Use `async with async_playwright()`.
- Include necessary imports.
- Ensure it is a complete, runnable script for this single test case.

**Output Requirements:**
Respond ONLY with a JSON object containing:
1. `"status"`: "PASS"
2. `"message"`: "Code generated"
3. `"evidence"`: "" (Empty string)
4. `"automation_code"`: the full Python code.
"""
        else: # Default "all" mode (Legacy support)
            task_description = f"""
**Task Assignment:**
{json.dumps(task, indent=2)}

**Long-term Memory Context (Relevant past test cases):**
{ltm_context}

**Test Engineering SOP (Rules):**
{prompt_rules}

**Your Role:**
You are a Senior SDET. Produce BOTH a Markdown test script and a Playwright Python automation script.

**Mandatory Deliverables (JSON Output):**
1. `"status"`: "PASS"
2. `"message"`: "Full bundle generated"
3. `"evidence"`: The full Markdown test document.
4. `"automation_code"`: The Playwright Python script.
"""
        # Cấu định Schema đầu ra cho SDET
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "SDETResponse",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "message": {"type": "string"},
                        "evidence": {"type": "string"},
                        "automation_code": {"type": "string"}
                    },
                    "required": ["status", "message", "evidence", "automation_code"]
                }
            }
        }

        # Thực thi LLM với vòng lặp Tool-calling (Centralized in AbstractAgent)
        response_message = await self.run_with_tools(
            system_prompt,
            task_description,
            max_steps=5,
            response_format=response_format
        )
        
        if not response_message:
            return {"status": "FAIL", "message": "Max tool steps reached or LLM error.", "evidence": ""}
            
        # Xử lý kết quả cuối cùng
        try:
            content = self.cut_thinking_step(response_message.content)
            result = json.loads(self._clean_json_string(content))
        except Exception as e:
            print(f"ERROR: SDET JSON Parse Error: {e}")
            result = {
                "status": "FAIL",
                "message": f"Error parsing SDET JSON: {str(e)}",
                "evidence": response_message.content,
                "automation_code": ""
            }
        
        # Ghi log
        if self.memory.shared_memory:
            self.memory.shared_memory.write_to_shared_log(
                self.profile['name'], 
                f"Task {task.get('id')} thực thi xong. Trạng thái: {result.get('status')}"
            )
        return result
