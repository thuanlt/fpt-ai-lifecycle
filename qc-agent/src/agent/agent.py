# ./agent/agent.py.v2
from abc import ABC, abstractmethod
from memory import MemoryManager
from memory.shared_memory import SharedMemory
from utils.logger import Logger
from models import ModelInfo
import json
import config

class AbstractAgent(ABC):
    def __init__(self, 
                 agent_profile: dict,
                 model_info: ModelInfo = None,
                 mcp_clients: list = None, 
                 shared_memory: SharedMemory = None, 
                 logger: Logger = None):
        self.profile = agent_profile
        self.memory = MemoryManager(shared_memory)
        self.mcp_clients = mcp_clients if mcp_clients else []
        if not model_info:
            model_info = ModelInfo()
            
        # Tự động điền API Key và Base URL từ config nếu bị thiếu
        if not model_info.model_name:
            model_info.model_name = getattr(config, 'LLM_MODEL_NAME', 'Qwen3-32B')
        if not model_info.api_key or model_info.api_key == "faked":
            model_info.api_key = getattr(config, 'FPT_API_KEY', '')
        if not model_info.base_url or 'localhost:4000' in model_info.base_url or not model_info.base_url:
            model_info.base_url = getattr(config, 'FPT_API_BASE', '')

        self.model_info = model_info
        
        # Tạo URL đầy đủ cho chat completions (Dùng requests, không dùng OpenAI SDK)
        base_url = self.model_info.base_url.rstrip("/")
        if "/v1" not in base_url:
            base_url += "/v1"
        self.endpoint_url = f"{base_url}/chat/completions"

        self.logger = logger
        self.tools = None
        self.functions = None
        self.map_tool_mcp = {}


    def _clean_json_string(self, text: str) -> str:
        """Loại bỏ các khối markdown ```json ... ``` hoặc ``` ... ``` nếu có."""
        if not text:
            return ""
        # Tìm nội dung giữa cặp ```json hoặc ```
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            return json_match.group(1).strip()
        # Nếu không có backticks, loại bỏ phần text thừa trước/sau cặp ngoặc {...}
        first_curly = text.find('{')
        last_curly = text.rfind('}')
        if first_curly != -1 and last_curly != -1:
            return text[first_curly:last_curly+1].strip()
        return text.strip()

    async def _execute_llm_call(self, 
                               system_prompt: str = None, 
                               user_prompt: str = None, 
                               messages: list = None,
                               use_tool: bool = False, 
                               tool_choice: str = None, 
                               response_format: dict = None) -> any:
        import requests
        import json
        
        try:
            agent_name = self.profile.get('name', 'Unknown Agent')
            print(f"\n[AI-LOG] Agent '{agent_name}' calling model: {self.model_info.model_name}")
            
            headers = {
                "Authorization": f"Bearer {self.model_info.api_key}",
                "Content-Type": "application/json"
            }
            
            if messages:
                payload_messages = messages
            else:
                payload_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

            payload = {
                "model": self.model_info.model_name,
                "messages": payload_messages,
                "temperature": 0.0
            }
            
            # Thêm hỗ trợ Tools (Công cụ)
            if use_tool and self.tools:
                payload["tools"] = self.tools
                if tool_choice:
                    payload["tool_choice"] = tool_choice

            # Thêm response_format nếu được yêu cầu
            if response_format:
                payload["response_format"] = response_format

            # Gọi API thực tế với cơ chế Retry
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = requests.post(
                        self.endpoint_url, 
                        headers=headers, 
                        json=payload, 
                        timeout=300.0 # Tăng timeout lên 5 phút
                    )
                    break # Thành công, thoát vòng lặp
                except requests.exceptions.ReadTimeout:
                    if attempt < max_retries:
                        print(f"[AI-LOG] WARNING: Model responding slowly (ReadTimeout), retrying attempt {attempt + 1}/{max_retries}...")
                        continue
                    else:
                        print(f"[AI-LOG] ERROR: System error calling Model: Read timed out after {max_retries} retries.")
                        return None
                except Exception as e:
                    print(f"[AI-LOG] ERROR: Connection error calling Model: {e}")
                    return None
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"[AI-LOG] ERROR: API Error: {error_msg}")
                return None
            
            result = response.json()
            message_data = result.get("choices", [{}])[0].get("message", {})
            content = message_data.get("content", "")
            tool_calls = message_data.get("tool_calls", None)
            
            print(f"[AI-LOG] DONE: Response received from {self.model_info.model_name}")
            
            # Xử lý kết quả (Clean JSON nếu cần)
            if response_format and content:
                content = self._clean_json_string(content)
            
            # Giả lập cấu trúc OpenAI để ko hỏng code cũ
            class MockToolCall:
                class Function:
                    def __init__(self, name, arguments):
                        self.name = name
                        self.arguments = arguments
                def __init__(self, tc_data):
                    self.id = tc_data.get("id")
                    self.type = "function"
                    func_data = tc_data.get("function", {})
                    self.function = self.Function(func_data.get("name"), func_data.get("arguments"))
            
            class MockMessage:
                def __init__(self, content, tc_raw):
                    self.content = content
                    self.tool_calls = [MockToolCall(tc) for tc in tc_raw] if tc_raw else None
                    self.role = "assistant"

            class MockChoice:
                def __init__(self, content, tc_raw):
                    self.message = MockMessage(content, tc_raw)

            class MockResponseWrapper:
                def __init__(self, content, tc_raw):
                    self.choices = [MockChoice(content, tc_raw)]
            
            return MockResponseWrapper(content, tool_calls)

        except Exception as e:
            print(f"[AI-LOG] ERROR: System error calling Model: {str(e)}")
            if self.logger:
                self.logger.console.print(f"[bold red]LLM Call Error: {str(e)}[/bold red]")
            return None

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass

    @abstractmethod
    def agent_as_a_function_description(self) -> dict:
        pass

    async def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        if tool_name not in self.map_tool_mcp:
            return {"error": f"Tool '{tool_name}' not found or MCP server disconnected.", "details": "The following tools are available: " + ", ".join(self.map_tool_mcp.keys())}
        return await self.map_tool_mcp[tool_name].execute_tool(tool_name, parameters)

    def cut_thinking_step(self, response_str: str) -> str:
        if not response_str:
            return ""
        if '</think>' in response_str:
            return response_str[response_str.find('</think>') + 8:].strip()
        return response_str.strip()

    async def initialize_tools(self):
        """
        Chủ động lấy danh sách tool từ các MCP client đã kết nối.
        Phương thức này phải được gọi sau khi các client đã được "enter".
        """
        if self.tools is None: # Chỉ chạy nếu self.tools chưa được khởi tạo
            self.tools = []
            if not self.mcp_clients:
                if self.logger:
                    self.logger.console.print(f"[yellow]Warning: Agent {self.profile.get('name')} has no MCP clients.[/yellow]")
                return

            if self.logger:
                self.logger.console_log(0, self.profile['name'], "Initializing tools from connected MCP clients...")
            
            for client in self.mcp_clients:
                if client.is_initialized:
                    openai_tools = await client.list_openai_tools()
                    self.tools.extend(openai_tools)
                    for tool in openai_tools:
                        self.map_tool_mcp[tool["function"]["name"]] = client
                else:
                    target = client.config.get("url") or client.config.get("file")
                    if self.logger:
                        self.logger.console.print(f"[bold red]Error: MCP client ({client.protocol_type}) for {target} is not initialized.[/bold red]")
            
            if self.logger:
                self.logger.console_log(0, self.profile['name'], f"Successfully initialized {len(self.tools)} tools.")

    async def run_with_tools(self, system_prompt: str, user_prompt: str, max_steps: int = 5, response_format: dict = None) -> any:
        """
        Thực thi agent với vòng lặp tool-calling và duy trì context (messages).
        """
        await self.initialize_tools()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        current_step = 0
        while current_step < max_steps:
            current_step += 1
            print(f"[DEBUG-AGENT] Step {current_step}/{max_steps}...")
            
            # Chỉ dùng response_format ở bước cuối HOẶC nếu LLM không gọi tool
            is_final = (current_step == max_steps)
            
            llm_response = await self._execute_llm_call(
                messages=messages,
                use_tool=True if self.tools else False,
                response_format=response_format if is_final else None
            )
            
            if not llm_response:
                return None
                
            message = llm_response.choices[0].message
            
            # Thêm phản hồi của assistant vào messages
            assistant_msg = {"role": "assistant", "content": message.content}
            if hasattr(message, 'tool_calls') and message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            messages.append(assistant_msg)

            # Nếu có Tool Call
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments
                    print(f"[DEBUG-AGENT] TOOL: Calling tool: {tool_name}({arguments})")
                    
                    tool_result = await self.execute_tool(tool_name, arguments)
                    
                    # Thêm phản hồi của tool vào messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                    })
            else:
                # Không có tool call, coi như kết quả cuối cùng
                return message
        
        return None