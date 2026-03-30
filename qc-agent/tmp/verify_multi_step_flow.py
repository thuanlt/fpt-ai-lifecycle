import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.test_utils import split_test_cases

async def verify_multi_step_logic():
    # 1. Mock Forensic Script from Agent
    evidence = """
# Login Feature
- [NEW] Test Case 1: Valid Login
    - Step 1: Open login page
    - Step 2: Enter credentials
- [NEW] Test Case 2: Invalid Login
    - Step 1: Open login page
    - Step 2: Enter wrong credentials
"""
    
    # 2. Split (as done in fast_track_endpoint.py)
    split_results = split_test_cases(evidence, "")
    assert len(split_results) == 2
    
    # 3. Mock separate Code Gen for each TC
    for i, tc in enumerate(split_results):
        # In reality, this would be an LLM call
        tc["automation_code"] = f"print('Automation for {tc['description']}')"
        
    # 4. Final aggregation check
    results = [{
        "task_id": "TASK_1",
        "status": "PASS",
        "test_cases": split_results
    }]
    
    # Print sample JSON that UI will receive
    print(json.dumps(results, indent=2))
    
    # Check structure
    assert results[0]["test_cases"][0]["id"] == "NEW"
    assert "Test Case 1" in results[0]["test_cases"][0]["description"]
    assert "Automation for Test Case 2" in results[0]["test_cases"][1]["automation_code"]
    
    print("\n✅ Verification SUCCESS: Multi-step logic matches requirements.")

if __name__ == "__main__":
    asyncio.run(verify_multi_step_logic())
