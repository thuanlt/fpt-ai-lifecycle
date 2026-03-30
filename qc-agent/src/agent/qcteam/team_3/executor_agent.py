# src/agent/qcteam/team_3/executor_agent.py
import json
import config
from agent import AbstractAgent
from agent.qcteam.tool_use_agents.browser_use_agent import BrowserUseAgent
from agent.qcteam.tool_use_agents.file_manager_agent import FileManagerAgent
from agent.qcteam.tool_use_agents.code_execute_agent import CodeExecuteAgent
from prompt.prompt_builder import builder
from tools.mcpclient import MCPClient
from pydantic import BaseModel

class Task(BaseModel):
    agent_name: str
    task_description: str

class ExecutorAgent(AbstractAgent):
    """
    Receives an analysis and a specific next action from the VerifierAgent.
    Its job is to delegate this action to the most appropriate specialized agent
    (e.g., BrowserUseAgent, FileManagerAgent).
    """
    def __init__(self, agent_profile: dict, logger=None, shared_memory=None):
        super().__init__(agent_profile, logger=logger, shared_memory=shared_memory)
        self.logger = logger
        self.shared_memory = shared_memory

        # Initialize MCP clients for sub-agents
        self.browser_use_clients = [
            MCPClient(server_config)
            for server_name, server_config in config.MCP_SERVERS_CONFIG.items()
            if server_name == "playwright"
        ]
        self.file_manager_clients = [
            MCPClient(server_config)
            for server_name, server_config in config.MCP_SERVERS_CONFIG.items()
            if server_name == "filesystem"
        ]
        self.code_execute_clients = [
            MCPClient(server_config)
            for server_name, server_config in config.MCP_SERVERS_CONFIG.items()
            if server_name == "bash-server"
        ]

        # Initialize sub-agents that this executor can delegate to
        self.browser_use_agent = BrowserUseAgent(
            agent_profile=builder.load_agent_profile("browser_use_agent"),
            mcp_clients=self.browser_use_clients,
            shared_memory=self.shared_memory,
            logger=self.logger
        )
        self.file_manager_agent = FileManagerAgent(
            agent_profile=builder.load_agent_profile("file_manager_agent"),
            mcp_clients=self.file_manager_clients,
            shared_memory=self.shared_memory,
            logger=self.logger
        )
        self.code_execute_agent = CodeExecuteAgent(
            agent_profile=builder.load_agent_profile("code_execute_agent"),
            mcp_clients=self.code_execute_clients,
            shared_memory=self.shared_memory,
            logger=self.logger
        )
        self.delegated_agents = {
            self.browser_use_agent.profile["name"]: self.browser_use_agent,
            self.file_manager_agent.profile["name"]: self.file_manager_agent,
            self.code_execute_agent.profile["name"]: self.code_execute_agent,
        }

    async def initialize_delegated_tools(self):
        mcp_plugins = [] 

        for client in self.browser_use_clients:
            await client.__aenter__()
            mcp_plugins.append(client)
        for client in self.file_manager_clients:
            await client.__aenter__()
            mcp_plugins.append(client)
        for client in self.code_execute_clients:
            await client.__aenter__()
            mcp_plugins.append(client)


        """Initializes the tools for all delegated agents."""
        await self.browser_use_agent.initialize_tools()
        await self.file_manager_agent.initialize_tools()
        await self.code_execute_agent.initialize_tools()

        # The Executor's "tools" are the agents it can call
        self.tools = [
            self.browser_use_agent.agent_as_a_function_description(),
            self.file_manager_agent.agent_as_a_function_description(),
            self.code_execute_agent.agent_as_a_function_description(),
        ]

        self.logger.console.print(f"[bold green]ExecutorAgent initialized with tools: {[tool['function']['name'] for tool in self.tools]}[/bold green]")

        return mcp_plugins

    def agent_as_a_function_description(self) -> dict:
        return {} # Not designed to be called by others

    async def run(self, step_index: int, analysis: str, next_action: str) -> dict:
        self.logger.console_log(step_index, self.profile['name'], f"Executing action: {next_action}")

        task_description = f"""
**Analysis of Current State:**
{analysis}

**Action to Execute:**
{next_action}

**Your Task:**
Based on the "Action to Execute", select the ONLY ONE tool to execute the task.
"""
        
        system_prompt = self.memory.assemble_prompt(self.profile, task_description)
        decision_response = await self._execute_llm_call(
            system_prompt, task_description, use_tool=True, tool_choice='required'
        )

        if not decision_response or not decision_response.choices[0].message.tool_calls:
            error_msg = "Executor LLM failed to select a tool/agent."
            self.logger.console.print(f"[bold red]ExecutorAgent Error: {error_msg}[/bold red]")
            return {"status": "error", "details": error_msg}

        try:
            tool_result = []
            if decision_response.choices[0].message.tool_calls is not None:
                for tool_call in decision_response.choices[0].message.tool_calls:
                # tool_call = decision_response.choices[0].message.tool_calls[0]
                    agent_to_call_name = tool_call.function.name
                    agent_args = json.loads(tool_call.function.arguments)

                    print(f"ExecutorAgent delegating to {agent_to_call_name} with args: {agent_args}")

                    agent_to_run = self.delegated_agents.get(agent_to_call_name)
                    if not agent_to_run:
                        raise ValueError(f"Agent '{agent_to_call_name}' not found.")

                    self.logger.console_log(
                        step_index,
                        self.profile['name'],
                        f"Delegating to {agent_to_call_name} with args: {agent_args}"
                    )
                    # Execute the delegated agent's run method
                    result = await agent_to_run.run(step_index=step_index, **agent_args)
                    # return {"status": "success", "agent_called": agent_to_call_name, "result": result}
                    tool_result.append({
                        "status": "success",
                        "agent_called": agent_to_call_name,
                        "result": result
                    })
            
            return tool_result

        except Exception as e:
            error_msg = f"Failed to execute delegated agent call: {e}"
            self.logger.console.print(f"[bold red]ExecutorAgent Error: {error_msg}[/bold red]")
            return [{"status": "error", "details": error_msg}]