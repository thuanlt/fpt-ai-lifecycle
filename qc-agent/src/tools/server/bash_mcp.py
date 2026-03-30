import subprocess
import os
import asyncio
import sys
from typing import Tuple
from mcp.server.fastmcp import FastMCP
import anyio

# Create a Model-Context-Protocol (MCP) server
mcp = FastMCP("Bash")

# Global variable for working directory
GLOBAL_CWD = os.getcwd()

@mcp.tool()
async def set_cwd(path: str) -> str:
    """Set the global working directory for bash/python commands."""
    global GLOBAL_CWD
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    GLOBAL_CWD = path
    return f"Working directory set to: {GLOBAL_CWD}"

@mcp.tool()
async def execute_bash(cmd: str) -> Tuple[str, str]:
    """Run a bash/shell command."""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
        cwd=GLOBAL_CWD
    )
    stdout, stderr = process.communicate()
    return stdout, stderr

@mcp.tool()
async def execute_python(code: str) -> Tuple[str, str]:
    """Execute a Python code snippet directly."""
    # Use a temporary file for execution
    tmp_file = os.path.join(GLOBAL_CWD, "tmp_snippet.py")
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    process = subprocess.Popen(
        [sys.executable, tmp_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=GLOBAL_CWD
    )
    stdout, stderr = process.communicate()
    os.remove(tmp_file)
    return stdout, stderr

async def create_stdio_streams():
    c_write, s_read = anyio.create_memory_object_stream(50)
    s_write, c_read = anyio.create_memory_object_stream(50)
    async def run_server_task():
        await mcp._mcp_server.run(
            s_read,
            s_write,
            mcp._mcp_server.create_initialization_options()
        )
    asyncio.create_task(run_server_task())
    return c_read, c_write

if __name__ == "__main__":
    import sys
    mcp.run()