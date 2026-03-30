import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.utils import jira_client
    print("Checking Project ID for 'NCPP'...")
    pid = jira_client.get_project_id_by_key("NCPP")
    print(f"Found Project ID: {pid}")
    
    # Also check if we can get test case statuses
    from src.config import config
    url = f"{config.JIRA_URL}/rest/tests/1.0/project/{pid}/testcasestatus"
    res = config.jira_session.get(url, auth=jira_client.account)
    print(f"Statuses Response: {res.status_code}")
    if res.status_code == 200:
        print(f"Statuses: {res.json()}")
        
    url_prio = f"{config.JIRA_URL}/rest/tests/1.0/project/{pid}/testcasepriority"
    res_prio = config.jira_session.get(url_prio, auth=jira_client.account)
    print(f"Priorities Response: {res_prio.status_code}")
    if res_prio.status_code == 200:
        print(f"Priorities: {res_prio.json()}")

except Exception as e:
    print(f"Error: {e}")
