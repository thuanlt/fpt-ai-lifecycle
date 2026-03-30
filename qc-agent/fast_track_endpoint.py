"""
Fast Track Endpoint Implementation
Receive request from UI and execute Fast Track flow:
FastPlannerAgent -> SeniorTesterAgent -> Integration
"""

import asyncio
import json
import sys
import os
from flask import Flask, request, jsonify

# Thêm src vào path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from agent.fast_planner import FastPlannerAgent
from agent.workers.senior_tester import SeniorTesterAgent
from utils.comms import send_markdown_summary
from utils.jira_client import update_test_cycle_status
from models.model_info import ModelInfo
import config
from utils.test_utils import split_test_cases, save_automation_code_to_file

app = Flask(__name__)

async def run_fast_track_logic(data):
    """
    Core logic for Fast Track Testing.
    Returns a result dictionary.
    """
    import re
    from memory.shared_memory import SharedMemory
    from tools.mcpclient import MCPClient
    from contextlib import AsyncExitStack
    
    instruction = data.get('instruction')
    cycle_id = data.get('cycle_id', 'NCPP-C123')
    project_key = data.get('project_key', 'NCPP')
    planner_model_choice = data.get('planner_model')
    tester_model_choice = data.get('tester_model')

    if not instruction:
        return {"error": "Missing instruction."}
            
    # 1. Extract IDs and Fetch Real Metadata
    found_cycle = re.search(r'NCPP-C\d+', instruction)
    found_case = re.search(r'NCPP-T\d+', instruction)
    extracted_cycle_id = found_cycle.group(0) if found_cycle else cycle_id
    extracted_test_case_id = found_case.group(0) if found_case else None

    jira_metadata = {}
    if extracted_test_case_id:
        try:
            from utils import jira_client
            print(f"[DEBUG] Fetching actual info for Test Case: {extracted_test_case_id}")
            case_info = jira_client.get_test_case_info(extracted_test_case_id)
            jira_metadata = {
                "name": case_info.get("name", "Unknown Case"),
                "objective": case_info.get("objective", ""),
                "precondition": case_info.get("precondition", ""),
                "project_key": project_key,
                "jira_id": extracted_test_case_id
            }
        except Exception as e:
            print(f"[DEBUG] Could not fetch metadata from Jira: {e}")

    final_metadata = {
        "name": jira_metadata.get("name", "Generated Flow"),
        "cycle_id": extracted_cycle_id,
        "project_key": project_key,
        "jira_metadata": jira_metadata,
        "api_spec": "N/A",
        "ui_xpath": "N/A"
    }
        
    shared_memory = SharedMemory()
    
    # --- 2. Initialize MCP Clients ---
    mcp_clients = []
    mcp_configs = getattr(config, 'MCP_SERVERS_CONFIG', {})
    for name, cfg in mcp_configs.items():
        try:
            print(f"[DEBUG] Initializing MCP Client: {name}")
            client = MCPClient(cfg)
            mcp_clients.append(client)
        except Exception as e:
            print(f"[DEBUG] Could not initialize MCP Client {name}: {e}")

    async with AsyncExitStack() as stack:
        # Kết nối TẤT CẢ MCP clients
        print(f"[DEBUG] Connecting to {len(mcp_clients)} MCP servers...")
        for client in mcp_clients:
            try:
                await stack.enter_async_context(client)
            except Exception as e:
                print(f"Error connecting to MCP Client: {e}")

        # --- 3. Run Planner ---
        final_planner_model = planner_model_choice or getattr(config, 'FAST_PLANNER_MODEL', 'Qwen3-32B')
        print(f"\n[DEBUG] 1. Launching Fast Planner ({final_planner_model})")
        planner_model_info = ModelInfo(model_name=final_planner_model)
        planner = FastPlannerAgent(shared_memory=shared_memory, model_info=planner_model_info)
        planner.mcp_clients = mcp_clients
        await planner.initialize_tools()
        
        print(f"[DEBUG-INPUT] Instruction: {instruction}")
        batch_task = await planner.run(instruction, final_metadata)
        print(f"[DEBUG-OUTPUT] Planner generated tasks: {len(batch_task.get('tasks', [])) if batch_task else 0}")
            
        if not batch_task:
            return {"error": "Fast Planner failed to parse batch task."}
            
        tasks = batch_task.get("tasks", [])
            
        # --- 4. Run Senior Testers ---
        final_tester_model = tester_model_choice or getattr(config, 'SENIOR_TESTER_MODEL', 'Qwen3-32B')
        print(f"\n[DEBUG] 2. Starting execution of tasks with Senior Tester ({final_tester_model})...")
        tester_model_info = ModelInfo(model_name=final_tester_model)
        senior_tester = SeniorTesterAgent(
            shared_memory=shared_memory, 
            model_info=tester_model_info,
            mcp_clients=mcp_clients
        )
        await senior_tester.initialize_tools()
            
        results = []
        overall_pass = True
        for i, task in enumerate(tasks):
            print(f"[DEBUG] --- Executing Task {i+1}/{len(tasks)}: {task.get('id')} ---")
            
            task['mode'] = 'generate_script'
            print(f"[DEBUG-INPUT] Generating script for task {task.get('id')}")
            worker_result = await senior_tester.run(task)
            evidence = worker_result.get("evidence", "")
            print(f"[DEBUG-OUTPUT] Script generated (length: {len(evidence)})")
            
            split_results = split_test_cases(evidence, "")
            task_test_cases = []
            for j, tc in enumerate(split_results):
                print(f"[DEBUG-INPUT] Generating code for TC {j+1}: {tc.get('description')}")
                code_task = task.copy()
                code_task['mode'] = 'generate_code'
                code_task['tc_evidence'] = tc.get('evidence', '')
                
                code_result = await senior_tester.run(code_task)
                tc_code = code_result.get("automation_code", "")
                tc["automation_code"] = tc_code
                print(f"[DEBUG-OUTPUT] Code generated for TC {j+1}")
                
                if tc_code:
                    filepath = save_automation_code_to_file(
                        task_id=task.get('id', 'unknown'),
                        tc_index=j+1,
                        code=tc_code,
                        working_dir=getattr(config, 'WORKING_DIR', os.getcwd())
                    )
                    tc["code_file"] = filepath
                
                task_test_cases.append(tc)
            
            results.append({
                "task_id": task.get('id'),
                "status": worker_result.get("status"),
                "tester": task.get("tester"),
                "target": task.get("target"),
                "jira_test_case_id": task.get("jira_test_case_id"),
                "test_cases": task_test_cases
            })
            if worker_result.get("status") != "PASS":
                overall_pass = False
                    
        # --- 5. Integration ---
        total = len(tasks)
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = total - passed
        
        jira_updated = ""
        if extracted_cycle_id:
            jira_updated = f"{getattr(config, 'JIRA_URL', '')}/secure/Tests.jspa#/testCycle/{extracted_cycle_id}"
            
        from utils.comms import send_markdown_summary
        send_markdown_summary(total, passed, failed, jira_updated)
            
        return {
            "overall_status": "PASS" if overall_pass else "FAIL",
            "batch_task": batch_task,
            "results": results,
            "jira": jira_updated
        }


# The Flask route and server logic have been moved to web_ui/server.py
# for 120B-class agent consistency and native async support.