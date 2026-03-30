import re

def split_test_cases(evidence: str, automation_code: str):
    # Pattern: "- [ID] Description" at the start of a line
    # Sometimes there's more indentation or no brackets
    tc_pattern = re.compile(r'^\s*-\s*\[?(NEW|NCPP-T\d+)?\]?\s*(.*)$', re.MULTILINE)
    
    # Actually, a better way to split is to look for the [NEW] marker as a boundary
    # Let's try splitting by the marker itself
    
    # We want to keep the header with the test case
    parts = re.split(r'(?=\s*-\s*\[?(?:NEW|NCPP-T\d+)\]?)', evidence)
    # Remove early parts that don't start with - [NEW]
    parts = [p.strip() for p in parts if p.strip() and (p.strip().startswith('-') or '[NEW]' in p or 'NCPP-T' in p)]
    
    print(f"Split into {len(parts)} parts")
    for i, p in enumerate(parts):
        print(f"Part {i+1} starts with: {p[:50]}...")

evidence_from_img = """
# Login Feature
## UI/UX
### Page Load
- [NEW] Verify login page displays all required UI elements
    - 1. Navigate to the login page URL
        - => The page loads successfully
## Validation
### Empty Fields
- [NEW] Attempt login with both username and password fields empty
    - 1. Leave both fields empty
"""

split_test_cases(evidence_from_img, "")
