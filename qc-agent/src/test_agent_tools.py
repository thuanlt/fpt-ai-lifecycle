import asyncio
import os
import sys
import json

# Disable proxy for local connections to avoid issues with Qdrant/MCP
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# Add project root to sys.path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from agent.workers.senior_tester import SeniorTesterAgent
from models.model_info import ModelInfo
from memory.shared_memory import SharedMemory
from tools.mcpclient import MCPClient
from contextlib import AsyncExitStack
import config

async def test_senior_tester_with_tools():
    print("🚀 Starting Verification Test for SeniorTesterAgent with Tools...")
    
    shared_memory = SharedMemory()
    model_info = ModelInfo(model_name=getattr(config, 'SENIOR_TESTER_MODEL', 'Qwen3-32B'))
    
    # Configure MCP Clients (using direct bash for simplicity in test)
    mcp_configs = {
        "bash": {
            "protocol": "direct",
            "file": "src/tools/server/bash_mcp.py"
        }
    }
    
    mcp_clients = []
    for name, cfg in mcp_configs.items():
        client = MCPClient(cfg)
        mcp_clients.append(client)
        
    async with AsyncExitStack() as stack:
        print("🔌 Connecting to MCP servers...")
        for client in mcp_clients:
            await stack.enter_async_context(client)
            
        agent = SeniorTesterAgent(
            model_info=model_info,
            shared_memory=shared_memory,
            mcp_clients=mcp_clients
        )
        
        # Simple task that requires using 'bash' tool to check a file or directory
        task = {
            "id": "test_verification_task",
            "description": "Please check the contents of the current directory using available tools and summarize what you see. Then generate a simple markdown test case for 'Directory Listing'.",
            "target": "System Shell",
            "mode": "all"
        }
        
        print(f"🤖 Running agent with task: {task['description']}")
        result = await agent.run(task)
        
        print("\n--- TEST RESULT ---")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        if result.get('evidence'):
            print(f"Evidence Length: {len(result.get('evidence'))}")
            print("Evidence Preview:")
            print(result.get('evidence')[:200] + "...")
        
        if result.get('status') == "PASS":
            print("\n✅ Verification SUCCESS: Agent used tools and produced a result.")
        else:
            print("\n❌ Verification FAILED: Agent did not produce a PASS status.")

if __name__ == "__main__":
    asyncio.run(test_senior_tester_with_tools())
