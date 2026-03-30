import re
import json

def split_test_cases(evidence, automation_code):
    """
    Splits the evidence and automation_code into individual test cases.
    Logic:
    - Evidence is split by lines starting with '- [NEW]' or similar.
    - Automation code is split based on some heuristic or markers.
    """
    # 1. Split evidence
    # Find all occurrences of "- [NEW]" or "- NEW" or "- [Jira ID]"
    # However, the user specifically mentioned "NEW".
    
    test_case_blocks = []
    
    # regex to find test case headers like "- [NEW] Description" or "- [ANY-ID] Description"
    # based on senior_tester.py: 87: - [Jira ID or [NEW]] [Test Case Description]
    tc_pattern = re.compile(r'^\s*-\s*\[(NEW|[^\]]+)\]\s+(.*)$', re.MULTILINE)
    
    matches = list(tc_pattern.finditer(evidence))
    
    if not matches:
        return [{"evidence": evidence, "automation_code": automation_code}]

    test_cases = []
    for i in range(len(matches)):
        start_pos = matches[i].start()
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(evidence)
        
        tc_id = matches[i].group(1)
        tc_desc = matches[i].group(2)
        tc_content = evidence[start_pos:end_pos].strip()
        
        test_cases.append({
            "id": tc_id,
            "description": tc_desc,
            "evidence": tc_content,
            "automation_code": "" # We will split this next
        })

    # 2. Split automation code
    # This is harder. Let's assume the agent provides code in blocks or functions.
    # For now, if we have N test cases, we might try to split the code into N parts
    # if there are clear delimiters like "# --- Test Case: ... ---"
    
    code_blocks = re.split(r'#\s*---\s*Test Case:.*---\s*', automation_code)
    # Remove empty first block if it exists
    if code_blocks and not code_blocks[0].strip():
        code_blocks.pop(0)

    if len(code_blocks) == len(test_cases):
        for i in range(len(test_cases)):
            test_cases[i]["automation_code"] = code_blocks[i].strip()
    else:
        # Fallback: keep the whole code for each test case or just for the first one
        # For MVP, maybe we just keep it as is if we can't split reliably.
        # But the user says "each testcase generates its own code file".
        # So we SHOULD split it.
        pass

    return test_cases

# Test data
evidence_data = """
# Login Feature
## Func
### Success Flow
- [NEW] Login with valid credentials
    - 1. Enter username
        - => Success
- [NEW] Login with invalid credentials
    - 1. Enter wrong password
        - => Error message shown
"""

automation_code_data = """
# --- Test Case: Login with valid credentials ---
import playwright
def test_valid():
    pass

# --- Test Case: Login with invalid credentials ---
def test_invalid():
    pass
"""

results = split_test_cases(evidence_data, automation_code_data)
print(json.dumps(results, indent=2))
