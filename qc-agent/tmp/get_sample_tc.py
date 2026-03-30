import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.utils import jira_client
    info = jira_client.get_test_case_info('NCPP-T301')
    with open("tmp/sample_tc.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("Sample TC info saved to tmp/sample_tc.json")
except Exception as e:
    print(f"Error: {e}")
