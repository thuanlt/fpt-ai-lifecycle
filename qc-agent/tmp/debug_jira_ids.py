import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.utils import jira_client
    from src.config import config
    
    pid = jira_client.get_project_id_by_key("NCPP")
    print(f"Project ID: {pid}")
    
    # Check statuses
    url = f"{config.JIRA_URL}/rest/tests/1.0/project/{pid}/testcasestatus"
    res = config.jira_session.get(url, auth=jira_client.account)
    statuses = res.json() if res.status_code == 200 else []
    
    # Check priorities
    url_prio = f"{config.JIRA_URL}/rest/tests/1.0/project/{pid}/testcasepriority"
    res_prio = config.jira_session.get(url_prio, auth=jira_client.account)
    priorities = res_prio.json() if res_prio.status_code == 200 else []
    
    debug_info = {
        "projectId": pid,
        "statuses": statuses,
        "priorities": priorities
    }
    
    with open("tmp/jira_debug_results.json", "w", encoding="utf-8") as f:
        json.dump(debug_info, f, indent=2, ensure_ascii=False)
        
    print("Debug info saved to tmp/jira_debug_results.json")

except Exception as e:
    print(f"Error: {e}")
