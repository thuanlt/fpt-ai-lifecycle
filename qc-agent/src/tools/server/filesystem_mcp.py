import os
import shutil
import glob
from mcp.server.fastmcp import FastMCP
import anyio
import asyncio

mcp = FastMCP("FileSystem")

@mcp.tool()
async def read_file(path: str) -> str:
    """Read full content of a file."""
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
async def write_file(path: str, content: str) -> str:
    """Write/overwrite content to a file."""
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"File written to {path}"

@mcp.tool()
async def append_file(path: str, content: str) -> str:
    """Append content to a file."""
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    with open(path, 'a', encoding='utf-8') as f:
        f.write("\n" + content)
    return f"Content appended to {path}"

@mcp.tool()
async def list_directory(path: str) -> str:
    """List directory contents."""
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    items = os.listdir(path)
    return "\n".join(items)

@mcp.tool()
async def delete_file(path: str) -> str:
    """Delete a file."""
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    os.remove(path)
    return f"File {path} deleted"

@mcp.tool()
async def search_files(pattern: str, recursive: bool = True) -> str:
    """Search for files matching a glob pattern."""
    files = glob.glob(pattern, recursive=recursive)
    return "\n".join(files)

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
    mcp.run()
