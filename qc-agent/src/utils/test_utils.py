import re
import os
import json
from datetime import datetime

def split_test_cases(evidence: str, automation_code: str):
    """
    Splits the evidence and automation_code into individual test cases while preserving hierarchy and context.
    Ensures that no test cases are missed across different sections.
    """
    lines = evidence.split('\n')
    common_header = []
    has_seen_tc = False
    
    # Track hierarchy
    h1, h2, h3 = "", "", ""
    
    test_cases = []
    current_tc = None
    
    # Delimiter for code
    delimiter = "# --- TEST_CASE_CODE_SPLIT ---"
    code_blocks = [block.strip() for block in automation_code.split(delimiter) if block.strip()]
    
    tc_marker_pattern = re.compile(r'^\s*-\s*\[(NEW|[^\]]+)\]\s*(.*)')
    
    for line in lines:
        # Detect headers
        if line.startswith('# '):
            h1 = line[2:].strip()
            h2, h3 = "", ""
        elif line.startswith('## '):
            h2 = line[3:].strip()
            h3 = ""
        elif line.startswith('### '):
            h3 = line[4:].strip()
            
        # Detect test cases
        tc_match = tc_marker_pattern.match(line)
        if tc_match:
            has_seen_tc = True
            tc_id = tc_match.group(1)
            tc_desc = tc_match.group(2).strip()
            
            # Close previous TC if any
            if current_tc:
                test_cases.append(current_tc)
            
            # Start new TC
            current_tc = {
                "id": tc_id,
                "description": tc_desc,
                "hierarchy": [h for h in [h1, h2, h3] if h],
                "lines": [line],
                "automation_code": ""
            }
        elif has_seen_tc:
            if current_tc:
                current_tc["lines"].append(line)
        else:
            # Still in common header
            common_header.append(line)
            
    # Add last TC if any
    if current_tc:
        test_cases.append(current_tc)
    
    # Post-process TCs to assemble evidence and link code
    header_text = "\n".join(common_header).strip()
    
    if not test_cases:
        return [{
            "id": "N/A",
            "description": "General Test Case",
            "evidence": evidence,
            "automation_code": automation_code
        }]
        
    for i, tc in enumerate(test_cases):
        # Assemble evidence: Header + TC path + TC lines
        path_context = ""
        if tc["hierarchy"]:
            path_context = "\n".join([("#" * (idx + 1) + " " + h) for idx, h in enumerate(tc["hierarchy"])])
            
        tc["evidence"] = f"{header_text}\n\n{path_context}\n\n" + "\n".join(tc["lines"]).strip()
        
        # Link code block
        if i < len(code_blocks):
            tc["automation_code"] = code_blocks[i]
        elif len(code_blocks) == 1:
            tc["automation_code"] = code_blocks[0]
            
        # Cleanup
        del tc["lines"]
        
    return test_cases

def save_automation_code_to_file(task_id: str, tc_index: int, code: str, working_dir: str = "."):
    """
    Saves automation code to a separate file in the tmp directory.
    """
    tmp_dir = os.path.join(working_dir, "tmp")
    try:
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
    except Exception as e:
        print(f"WARNING: Could not create tmp_dir at {tmp_dir} ({e}). Falling back to current directory.")
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_{task_id}_{tc_index}_{timestamp}.py"
    filepath = os.path.join(tmp_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
        
    return filepath
