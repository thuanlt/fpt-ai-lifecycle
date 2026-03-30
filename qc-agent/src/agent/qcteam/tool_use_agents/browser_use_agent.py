# ./agent/qcteam/qc_agent.py
import json
from agent import AbstractAgent
from memory.shared_memory import SharedMemory

class BrowserUseAgent(AbstractAgent):
    def __init__(self, agent_profile: dict, mcp_clients: list = None, shared_memory: SharedMemory = None, logger=None):
        super().__init__(agent_profile, mcp_clients, shared_memory, logger)

    def agent_as_a_function_description(self) -> dict:
        list_tool = ', '.join([key for key in self.map_tool_mcp.keys()])
        return {
            "type": "function",
            "function": {
                "name": self.profile['name'],
                "description": f"SPECIALIZE FOR WEB BROWSER USE, that automates tasks in a web browser to accomplish a high-level objective. Use this for navigating websites, filling forms, clicking buttons, and extracting information. This agent can use follow functions: {list_tool}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "A clear, natural language instruction of the objective to achieve in the browser. For example: 'Log into the internal dashboard and find the total number of new users for this month.'"
                        }
                    },
                    "required": ["task_description"]
                }
            }
        }

    async def run(self, step_index: int, task_description: str) -> dict:
        self.logger.console_log(step_index, self.profile['name'], f"Executing task: {task_description}")

        if not self.mcp_clients:
            return {"task": task_description, "status": "error", "details": "QCAgent has no MCP clients configured."}

        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        llm_response = await self._execute_llm_call(system_prompt, task_description, use_tool=True, tool_choice='required')

        if not llm_response:
            self.logger.log_agent_step(step_index, self.profile['name'], system_prompt, task_description, "LLM call failed.")
            return {"task": task_description, "status": "error", "details": "LLM call failed to determine tool."}

        response_message = llm_response.choices[0].message
        tool_results = []

        # print(response_message)

        if not response_message.tool_calls:
            self.logger.console.print("LLM decided not to call any tool.")
            tool_results.append({
                "status": "no_action", "details": "LLM did not select a tool.",
                "llm_message": response_message.content
            })
            self.memory.shared_memory.write_to_shared_log(
                agent_id=self.profile.get("name"),
                message="LLM did not select a tool.")
        else:
            for tool_call in response_message.tool_calls:
                print(f"tool {tool_call}")
                self.logger.console_log(step_index, "ToolCall", f"Executing tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
                tool_name = tool_call.function.name

                if tool_name == "gen_playwright_script":
                    gen_script_profile = {
                        "role": "Playwright typescript code generator",
                        "task": "You are a professional programmer in typescript and playwright tool. You are given list of steps of playwright outputs. Your task is create a typescript that mimic the behavior through list steps. User can use your script for later automation running.",
                        "Output": "You will output a typescript source code without any other information that break the code. User can use your source code immediately without any modification. Your source code must have guide line to run in a block of comment at the beginning of the file."
                    }

                    system_prompt = self.memory.assemble_prompt(gen_script_profile, task_description)
                    llm_response = await self._execute_llm_call(system_prompt, task_description)
                    response_message = llm_response.choices[0].message.content

                    return response_message
                else:
                    try:
                        parameters = json.loads(tool_call.function.arguments)
                        mcp_client = self.map_tool_mcp.get(tool_name)
                        execution_result = await mcp_client.execute_tool(tool_name, parameters)
                        execution_result['task'] = task_description
                        tool_results.append(execution_result)

                        self.memory.shared_memory.write_to_shared_log(
                            agent_id=self.profile.get("name"),
                            message=execution_result
                        )
                    except Exception as e:
                        error_detail = f"Failed during tool execution '{tool_name}': {e}"
                        tool_results.append({"task": task_description, "status": "error", "details": error_detail})

                        self.memory.shared_memory.write_to_shared_log(
                            agent_id=self.profile.get("name"),
                            message=error_detail
                        )

        self.logger.log_agent_step(
            step_index=step_index,
            agent_name=self.profile['name'],
            system_prompt=system_prompt,
            user_prompt=task_description,
            llm_response=response_message,
            tool_responses=tool_results
        )
        
        return tool_results

    async def initialize_tools(self):
        if self.tools is None:
            await super().initialize_tools()
            self.tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "gen_playwright_script",
                        "description": f"Generate playwright script in typescript from given usage history of playwright. The generated script will redo all recorded steps.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
            )