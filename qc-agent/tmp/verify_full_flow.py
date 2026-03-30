import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.test_utils import split_test_cases, save_automation_code_to_file

async def verify_output_format():
    evidence = """
# Login Feature
## UI/UX
- [NEW] Test Case 1
    - Step 1
- [NEW] Test Case 2
    - Step 2
"""
    automation_code = """
print("Code 1")
# --- TEST_CASE_CODE_SPLIT ---
print("Code 2")
"""
    
    # Simulate SeniorTesterAgent.run result
    worker_result = {
        "status": "PASS",
        "evidence": evidence,
        "automation_code": automation_code
    }
    
    # Simulate logic in fast_track_endpoint.py
    task = {"id": "TASK_1", "tester": "Senior Tester", "target": "Login", "jira_test_case_id": "T-123"}
    
    split_results = split_test_cases(worker_result["evidence"], worker_result["automation_code"])
    
    task_test_cases = []
    for j, tc in enumerate(split_results):
        # We don't need to actually save files for this JSON format check
        task_test_cases.append(tc)
        
    final_result = {
        "task_id": task.get('id'),
        "status": worker_result.get("status"),
        "tester": task.get("tester"),
        "target": task.get("target"),
        "jira_test_case_id": task.get("jira_test_case_id"),
        "test_cases": task_test_cases
    }
    
    print(json.dumps(final_result, indent=2))
    
    # Assertions
    assert len(final_result["test_cases"]) == 2
    assert final_result["test_cases"][0]["id"] == "NEW"
    assert "# Login Feature" in final_result["test_cases"][0]["evidence"]
    assert "Code 1" in final_result["test_cases"][0]["automation_code"]
    assert "Code 2" in final_result["test_cases"][1]["automation_code"]
    
    print("\n✅ Verification SUCCESS: JSON format is correct and headers are preserved.")

if __name__ == "__main__":
    asyncio.run(verify_output_format())
