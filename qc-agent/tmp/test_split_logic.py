import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.test_utils import split_test_cases, save_automation_code_to_file

def test_split_logic():
    print("--- Testing split_test_cases ---")
    
    evidence = """
# Login Feature
## Func
### Success Flow
- [NEW] Login with valid credentials
    - 1. Enter username
        - => Success
- [NCPP-T123] Login with invalid credentials
    - 1. Enter wrong password
        - => Error message shown
"""

    automation_code = """
import playwright
def test_valid():
    print("Valid credentials")

# --- TEST_CASE_CODE_SPLIT ---

def test_invalid():
    print("Invalid credentials")
"""

    results = split_test_cases(evidence, automation_code)
    
    print(f"Number of test cases found: {len(results)}")
    assert len(results) == 2, f"Expected 2 test cases, found {len(results)}"
    
    print(f"TC 1 ID: {results[0]['id']}")
    assert results[0]['id'] == 'NEW'
    
    print(f"TC 2 ID: {results[1]['id']}")
    assert results[1]['id'] == 'NCPP-T123'
    
    print(f"TC 1 Description: {results[0]['description']}")
    assert results[0]['description'] == 'Login with valid credentials'
    
    print(f"TC 1 Code contains 'test_valid': {'test_valid' in results[0]['automation_code']}")
    assert 'test_valid' in results[0]['automation_code']

    print(f"TC 2 Code contains 'test_invalid': {'test_invalid' in results[1]['automation_code']}")
    assert 'test_invalid' in results[1]['automation_code']

    print("✅ split_test_cases PASSED")

def test_file_saving():
    print("\n--- Testing save_automation_code_to_file ---")
    
    code = "print('Hello World')"
    task_id = "TASK_99"
    tc_index = 1
    
    working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filepath = save_automation_code_to_file(task_id, tc_index, code, working_dir)
    
    print(f"File saved to: {filepath}")
    assert os.path.exists(filepath), f"File {filepath} not found"
    
    with open(filepath, 'r') as f:
        content = f.read()
    assert content == code, f"File content mismatch: expected '{code}', found '{content}'"
    
    print("✅ save_automation_code_to_file PASSED")

if __name__ == "__main__":
    try:
        test_split_logic()
        test_file_saving()
        print("\n🎉 ALL TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
