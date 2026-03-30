import inspect
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Test")
print(f"run_stdio_async signature: {inspect.signature(mcp.run_stdio_async)}")
