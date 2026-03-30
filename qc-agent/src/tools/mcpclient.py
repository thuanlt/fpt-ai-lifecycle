import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client # <-- 1. IMPORT the stdio client
from mcp import types
from urllib.parse import urlparse
import json
from typing import List, Dict, Any

class MCPClient:
    """
    An enhanced MCP client that can connect to servers via HTTP, SSE, or Stdio
    based on a provided configuration dictionary.
    """
    def __init__(self, server_config: dict):
        if not server_config or not isinstance(server_config, dict):
            raise ValueError("A server configuration dictionary must be provided.")

        self.config = server_config
        self.protocol_type = self.config.get("protocol")

        if not self.protocol_type:
            raise ValueError("Server configuration must include a 'protocol' key ('http', 'sse', or 'stdio').")

        self._client = None
        self._session = None
        self.is_initialized = False
        print(f"Unified client configured for protocol: {self.protocol_type.upper()}")

    async def __aenter__(self):
        print(f"DEBUG: Connecting to MCP server via {self.protocol_type.upper()}...")
        try:
            if self.protocol_type == "http":
                url = self.config.get("url")
                if not url or urlparse(url).path != "/mcp":
                    raise ValueError("HTTP protocol requires a 'url' ending in /mcp")
                self._client = streamablehttp_client(url)
                self._read_stream, self._write_stream, _ = await self._client.__aenter__()

            elif self.protocol_type == "sse":
                url = self.config.get("url")
                if not url or urlparse(url).path != "/sse":
                    raise ValueError("SSE protocol requires a 'url' ending in /sse")
                self._client = sse_client(url)
                self._read_stream, self._write_stream = await self._client.__aenter__()
            
            elif self.protocol_type == "stdio": 
                command = self.config.get("command")
                args = self.config.get("args", [])
                server_params = StdioServerParameters(command=command, args=args)
                if not command:
                    raise ValueError("Stdio protocol requires a 'command' in the configuration.")
                self._client = stdio_client(server_params)
                self._read_stream, self._write_stream = await self._client.__aenter__()
            elif self.protocol_type == "direct":
                # Direct protocol for in-process MCP server (e.g., bash server)
                from importlib import import_module
                module_path = self.config.get("file")
                if not module_path:
                    raise ValueError("Direct protocol requires a 'file' path in the configuration.")
                module_name = module_path.replace('\\', '.').replace('/', '.')
                if module_name.endswith('.py'):
                    module_name = module_name[:-3]
                mcp_module = import_module(module_name)
                if not hasattr(mcp_module, 'create_stdio_streams'):
                    raise ValueError(f"The module '{module_path}' must define a 'create_stdio_streams' function.")
                self._read_stream, self._write_stream = await mcp_module.create_stdio_streams()
                print(f"DONE: Direct MCP server streams created from {module_path}")
            else:
                raise ValueError(f"Unsupported protocol type: '{self.protocol_type}'. Must be 'http', 'sse', or 'stdio'.")

        except Exception as e:
            print(f"ERROR: initializing MCP client: {e}")
            raise
        
        self._session = ClientSession(read_stream=self._read_stream, write_stream=self._write_stream)
        await self._session.__aenter__()
        try:
            print(f"DEBUG: Initializing MCP session...")
            # Set a timeout for initialization if possible, or just catch the cancellation
            await self._session.initialize()
            self.is_initialized = True
            print(f"DONE: MCP session (via {self.protocol_type.upper()}) initialized successfully.")
        except Exception as e:
            print(f"ERROR: Failed to initialize MCP session: {e}")
            self.is_initialized = False
        except BaseException as e:
            # Catch CancelledError (BaseException in Python 3.8+)
            print(f"WARNING: MCP session initialization was cancelled or interrupted: {e}")
            self.is_initialized = False
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._session:
                await self._session.__aexit__(exc_type, exc_val, exc_tb)
            if self._client:
                await self._client.__aexit__(exc_type, exc_val, exc_tb)
        except Exception as e:
            print(f"Closing MCP exception: {e}")
        self.is_initialized = False
        print(f"DEBUG: MCP connection (via {self.protocol_type.upper()}) closed.")

    async def list_tools(self) -> list:
        try:
            if not self.is_initialized:
                raise ConnectionError("Session not initialized.")
            print(f"DEBUG: Found {len(tools)} tools via {self.protocol_type.upper()}.")
            return tool_list
        except Exception as e:
            print(f"List tool exception {e}")
            return None
    
    async def list_tools_json(self) -> str:
        tools = await self.list_tools()
        return json.dumps([tool.name for tool in tools.tools], indent=2)

    async def list_openai_tools(self) -> List[Dict[str, Any]]:
        if hasattr(self, '_cached_openai_tools') and self._cached_openai_tools:
            return self._cached_openai_tools
            
        openai_formatted_tools = []
        tools = await self.list_tools()
        if tools is None:
            return openai_formatted_tools
        
        for tool in tools.tools:
            openai_formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            })
        self._cached_openai_tools = openai_formatted_tools
        return openai_formatted_tools

    async def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        if not self.is_initialized:
            raise ConnectionError("Session is not initialized.")
        
        parsed_params = parameters
        if isinstance(parameters, str):
            try:
                parsed_params = json.loads(parameters)
            except json.JSONDecodeError:
                error_msg = f"Invalid JSON format for parameters: {parameters}"
                return {"status": "error", "details": error_msg}
            
        try:
            result = await self._session.call_tool(tool_name, arguments=parsed_params)
            
            if result and not result.isError:
                content_block = result.content[0]
                if isinstance(content_block, types.TextContent):
                    final_result = content_block.text
                else:
                    final_result = str(content_block)
                return {"status": "success", "details": final_result}
            else:
                error_msg = f"Tool '{tool_name}' execution failed"
                return {"status": "error", "details": error_msg}
        except Exception as e:
            return {"status": "error", "details": str(e)}