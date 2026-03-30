import tools.mcpclient as mcpclient
import asyncio
import json

server_config = {
    "protocol": "http",
    "url": "http://localhost:8931/mcp"
}

async def main():
    async with mcpclient.MCPClient(server_config) as client:
        tools = await client.list_openai_tools()
        print(f"Tools: {json.dumps(tools, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())