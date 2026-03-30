import json
from agent import AbstractAgent
from memory.shared_memory import SharedMemory

class CodeExecuteAgent(AbstractAgent):
    def __init__(self, agent_profile: dict, mcp_clients: list = None, shared_memory: SharedMemory = None, logger=None):
        super().__init__(agent_profile, mcp_clients, shared_memory, logger)

    def agent_as_a_function_description(self) -> dict:
        list_tool = ', '.join([key for key in self.map_tool_mcp.keys()])
        return {
        "type": "function",
        "function": {
            "name": self.profile['name'],
            "description": f"SPECIALIZED FOR CODE EXECUTION such as running code snippets, executing scripts, or performing code-related tasks. This agent can use follow functions: {list_tool}",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "A specific, natural language command for the code execution task the tool need to do. Examples: 'Run the Python script at /scripts/analyze.py', 'Execute the code snippet \"print(\\'Hello World\\')\"', 'Run the shell command \"ls -la\" in the /data directory'."
                    }
                },
                "required": ["task_description"]
            }
        }
    }

    async def run(self, step_index: int, task_description: str) -> dict:
        self.logger.console_log(step_index, self.profile['name'], f"Executing task: {task_description}")

        if not self.mcp_clients:
            return {"status": "error", "details": "CodeExecuteAgent has no MCP clients configured."}

        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        llm_response = await self._execute_llm_call(system_prompt, task_description, use_tool=True, tool_choice='auto')

        if not llm_response:
            self.logger.log_agent_step(step_index, self.profile['name'], system_prompt, task_description, "LLM call failed.")
            return {"status": "error", "details": "LLM call failed to determine tool."}

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
                tool_args = json.loads(tool_call.function.arguments)
                try:
                    parameters = json.loads(tool_call.function.arguments)
                    mcp_client = self.map_tool_mcp.get(tool_name)
                    execution_result = await mcp_client.execute_tool(tool_name, parameters)
                    tool_results.append(execution_result)
                except Exception as e:
                    error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                    self.logger.console.print(f"[bold red]CodeExecuteAgent Error: {error_msg}[/bold red]")
                    tool_results.append({"status": "error", "details": error_msg})

                    self.memory.shared_memory.write_to_shared_log(
                        agent_id=self.profile.get("name"),
                        message=error_msg
                    )
        
        self.logger.log_agent_step(
            step_index,
            self.profile['name'],
            system_prompt,
            task_description,
            response_message.content if response_message else "No response",
            tool_results
        )

        return tool_results
    
