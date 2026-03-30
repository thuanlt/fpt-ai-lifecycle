from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import sys
import os
import json

# Đảm bảo có thể import được các module từ thư mục src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import config đúng đường dẫn
from src.config import config

from time import time
import uuid

account = HTTPBasicAuth(config.JIRA_USERNAME, config.JIRA_API_TOKEN)

def get_test_case_info(test_case_id: str):
    """Corresponds to the 'Get test case info' node."""
    url = f"{config.JIRA_URL}/rest/tests/1.0/testcase/{test_case_id}"
    params = {
        "fields": "id,projectId,archived,key,name,objective,majorVersion,latestVersion,precondition,folder(id,fullName),status,priority,estimatedTime,averageTime,componentId,owner,labels,customFieldValues,testScript(id,text,steps(index,description,text,expectedResult,testData,attachments,customFieldValues,id,stepParameters(id,testCaseParameterId,value),testCase(id,key,name,archived,majorVersion,latestVersion,parameters(id,name,defaultValue,index)))),testData,parameters(id,name,defaultValue,index),paramType"
    }
    headers = {
        "Accept": "application/json"
    }
    try:
        response = config.jira_session.get(url, params=params, headers=headers, auth=account)
        response.raise_for_status()
        print(f"DONE: Fetched test case info for {test_case_id}")
        return response.json()
    except requests.RequestException as e:
        print(f"ERROR: fetching test case info: {e}")
        raise

def get_test_cycle_info(test_cycle_id: str):
    """Corresponds to 'Get test cycle Id' and 'Get detail test cycle' nodes."""
    try:
        cycle_url = f"{config.JIRA_URL}/rest/tests/1.0/testrun/{test_cycle_id}"
        params = {
            "fields": "id,key,name,projectId,projectVersionId,environmentId,plannedStartDate,plannedEndDate,iteration(name),executionTime,estimatedTime"
        }
        headers = {
            "Accept": "application/json"
        }
        cycle_response = config.jira_session.get(cycle_url, params=params, headers=headers, auth=account)
        cycle_response.raise_for_status()
        cycle_data = cycle_response.json()
        
        items_url = f"{config.JIRA_URL}/rest/tests/1.0/testrun/{cycle_data['id']}/testrunitems"
        params = {
            "fields": "id,index,issueCount,$lastTestResult"
        }
        headers = {
            "Accept": "application/json"
        }
        items_response = config.jira_session.get(items_url, params=params, headers=headers, auth=account)
        items_response.raise_for_status()
        cycle_data['testRunItems'] = items_response.json()
        print(f"DONE: Fetched test cycle info and items for {test_cycle_id}")
        return cycle_data
    except requests.RequestException as e:
        print(f"ERROR: fetching test cycle info: {e}")
        raise

def create_test_execution(payload: dict):
    """Corresponds to the 'Create new execution' node."""
    url = f"{config.JIRA_URL}/rest/tests/1.0/testresult"
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = config.jira_session.post(url, json=payload, headers=headers, auth=account)
        response.raise_for_status()
        execution_data = response.json()
        print(f"DONE: Created new test execution with ID: {execution_data['id']}")
        return execution_data
    except requests.RequestException as e:
        print(f"ERROR: creating test execution: {e}")
        raise

def update_execution_status(payload: dict):
    """Corresponds to the 'Update execution status' node."""
    url = f"{config.JIRA_URL}/rest/tests/1.0/testresult"
    headers = {
        "Accept": "application/json"
    }

    try:
        response = config.jira_session.put(url, json=payload, headers=headers, auth=account)
        response.raise_for_status()
        print(f"DONE: Updated execution {payload['id']} with status {payload['testResult']}")
        return response.text
    except requests.RequestException as e:
        print(f"ERROR: updating execution status: {e}")
        raise

def add_test_case_to_cycle(test_cycle_id: str, test_case_key: str):
    """Gán một Test Case vào Test Cycle (Run) trong Zephyr Scale."""
    try:
        # 1. Lấy thông tin Cycle để có Numeric ID
        url_get = f"{config.JIRA_URL}/rest/tests/1.0/testrun/{test_cycle_id}"
        res_get = config.jira_session.get(url_get, auth=account)
        res_get.raise_for_status()
        cycle_numeric_id = res_get.json()["id"]
        
        # 2. Add Test Case vào Cycle
        url_add = f"{config.JIRA_URL}/rest/tests/1.0/testrun/{cycle_numeric_id}/testcase"
        payload = {"testCaseKeys": [test_case_key]}
        res_add = config.jira_session.post(url_add, json=payload, auth=account)
        
        if res_add.status_code == 201:
            print(f"DONE: Assigned {test_case_key} to Cycle {test_cycle_id}")
            return True
        else:
            print(f"WARNING: Could not assign {test_case_key} to Cycle: {res_add.text}")
            return False
    except Exception as e:
        print(f"ERROR: assigning Case to Cycle: {e}")
        return False

def parse_markdown_to_steps(markdown_text: str):
    """
    Trích xuất các bước test từ Markdown của AI.
    Biến mỗi dòng kết quả mong đợi (- => hoặc =>) thành một bước (step) riêng trên Jira 
    để người dùng có thể pass/fail từng ý nhỏ.
    """
    import re
    steps = []
    lines = markdown_text.split('\n')
    
    current_action_desc = ""
    
    # Regex tìm dòng bắt đầu bước mới: "1. Action" hoặc "Step 1. Action"
    step_start_pattern = re.compile(r'^\s*(?:Step\s+)?(\d+(?:\.\d+)?)\.\s+(.*)', re.IGNORECASE)
    # Regex tìm dòng kết quả: vế có => hoặc - =>
    result_pattern = re.compile(r'^\s*(-?\s*=>)\s*(.*)', re.IGNORECASE)
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("---") or "*Task Completed*" in line_clean:
            continue
            
        step_match = step_start_pattern.match(line_clean)
        res_match = result_pattern.match(line_clean)
        
        if step_match:
            # Ghi nhận Action mới
            current_action_desc = step_match.group(2).strip()
            # Chúng ta chưa tạo step ngay vì cần đợi kết quả đầu tiên đi cùng action này
            
        elif res_match:
            # Khi gặp một dòng kết quả (- => hoặc =>)
            symbol = res_match.group(1).strip()
            content = res_match.group(2).strip()
            full_res = f"{symbol} {content}"
            
            if current_action_desc:
                # Nếu đây là kết quả đầu tiên sau một Action
                steps.append({
                    "index": len(steps),
                    "description": current_action_desc,
                    "expectedResult": full_res
                })
                current_action_desc = "" # Xóa đi để các kết quả tiếp theo (nếu có) sẽ tạo step mới với desc rỗng
            else:
                # Nếu action desc đã dùng rồi hoặc chưa có (kết quả thứ 2, 3... của cùng 1 action)
                steps.append({
                    "index": len(steps),
                    "description": "-", # Để dấu gạch ngang hoặc rỗng cho các "step con"
                    "expectedResult": full_res
                })
        elif current_action_desc:
            # Đây là dòng mô tả thêm (ví dụ payload JSON) cho Action hiện tại
            # Sử dụng double <br /> để thông tin thoáng hơn theo yêu cầu
            current_action_desc += "<br /><br />" + line.strip()
                
    return steps

def format_jira_payload(execution_status: str, metadata: dict, log: str, screenshot_path: str = "") -> dict:
    """
    Chuẩn hóa dữ liệu payload cho Jira dựa trên kết quả Worker
    và metadata. Mapping priority, assignee.
    """
    priority = metadata.get("priority", "Medium")
    assignee = metadata.get("owner", "Unassigned")
    
    description = f"Status: {execution_status}\n\nLog:\n{log}"
    if screenshot_path:
        description += f"\n\nScreenshot attaches: {screenshot_path}"
        
    payload = {
        "fields": {
            "project": {"key": config.JIRA_PROJECT_KEY} if hasattr(config, 'JIRA_PROJECT_KEY') else {"key": "NCPP"},
            "summary": f"Automation Test Failed - {metadata.get('name', 'Unknown')}",
            "description": description,
            "issuetype": {"name": "Bug"},
            "priority": {"name": priority},
            # "assignee": {"name": assignee} # Assuming valid jira user name mapping exist
        }
    }
    return payload

def get_project_id_by_key(project_key: str):
    """Lấy Numeric ID của Project từ API JIRA."""
    url = f"{config.JIRA_URL}/rest/api/2/project/{project_key}"
    try:
        response = config.jira_session.get(url, auth=account)
        response.raise_for_status()
        return response.json().get("id")
    except Exception as e:
        print(f"WARNING: Could not fetch numeric projectId for {project_key}: {e}")
        return None

def create_zephyr_test_case(name: str, objective: str, project_key: str = None, metadata: dict = None, folder: str = ""):
    """
    Tạo một Test Case với payload tối giản và an toàn nhất để tránh lỗi 500 trên Zephyr Server.
    """
    url = f"{config.JIRA_URL}/rest/tests/1.0/testcase"
    project_key = project_key or getattr(config, 'JIRA_PROJECT_KEY', 'NCPP')
    metadata = metadata or {}
    
    # 0. Làm sạch objective
    clean_objective = objective.replace('\u2192', '->').replace('\u2011', '-')
    
    # Trích xuất Precondition
    precondition = ""
    import re
    pre_match = re.search(r'(?i)precondition[:\s]*(.*?)(?:\n\n|\n#|$)', clean_objective, re.DOTALL)
    if pre_match:
        precondition = pre_match.group(1).strip()

    # Trích xuất và chuẩn hóa steps
    steps_data = parse_markdown_to_steps(clean_objective)
    safe_steps = []
    for s in steps_data:
        # Chỉ gửi 3 trường cốt lõi nhất của 1 step
        safe_steps.append({
            "index": s["index"],
            "description": s["description"],
            "expectedResult": s["expectedResult"]
        })
    
    # Lấy numeric projectId (Bắt buộc)
    numeric_pid = get_project_id_by_key(project_key)
    if not numeric_pid:
        numeric_pid = 15234 # Fallback ID của dự án NCPP nếu lấy thất bại
        
    # Payload tối giản (Chỉ các trường chắc chắn được hỗ trợ POST)
    payload = {
        "name": name,
        "projectId": int(numeric_pid),
        "objective": clean_objective,
        "precondition": precondition,
        "status": {"id": 42},    # Draft
        "priority": {"id": 52},   # Normal
        "labels": metadata.get("labels", ["AI-Generated"]),
        "folder": {"fullName": folder} if folder else None
    }
    
    # Thêm steps nếu có
    if safe_steps:
        payload["testScript"] = {
            "stepByStepScript": {
                "steps": safe_steps
            }
        }
    
    print(f"[DEBUG] Sending SAFE payload to Zephyr: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        response = config.jira_session.post(url, json=payload, headers=headers, auth=account)
        
        if response.status_code != 201:
            print(f"WARNING: Jira API Error Code: {response.status_code}")
            print(f"WARNING: Response content: {response.text}")
            
            # Fallback sang projectKey nếu projectId bị từ chối
            if "projectId" in response.text or response.status_code == 400:
                print("Fallback to projectKey...")
                payload.pop("projectId", None)
                payload["projectKey"] = project_key
                response = config.jira_session.post(url, json=payload, headers=headers, auth=account)

        response.raise_for_status()
        case_data = response.json()
        print(f"DONE: Created Safe Zephyr Test Case: {case_data['key']}")
        return case_data['key']
    except Exception as e:
        print(f"ERROR: creating Zephyr Test Case: {e}")
        if 'response' in locals() and response is not None:
             print(f"--- Final Response Content ---\n{response.text}\n---------------------------")
        return None

def create_issue(summary: str, description: str, issue_type: str = "Bug", project_key: str = None):
    """Tạo một Issue mới trên Jira (Bug, Test, Task, etc.)"""
    project_key = project_key or getattr(config, 'JIRA_PROJECT_KEY', 'NCPP')
    url = f"{config.JIRA_URL}/rest/api/2/issue"
    
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type}
        }
    }
    
    try:
        response = config.jira_session.post(url, json=payload, headers={"Accept": "application/json"}, auth=account)
        response.raise_for_status()
        issue_data = response.json()
        print(f"DONE: Created new {issue_type} with Key: {issue_data['key']}")
        return issue_data['key']
    except Exception as e:
        print(f"ERROR: creating {issue_type}: {e}")
        return None

def sync_and_execute_test_case(cycle_id: str, test_case_id: str, status: str, log: str = ""):
    """
    Thực hiện trọn gói luồng Zephyr: Tìm trong Cycle -> Tạo Execution -> Cập nhật Trạng thái.
    """
    try:
        # 1. Lấy thông tin Case và Cycle để khớp ID nội bộ
        case_info = get_test_case_info(test_case_id)
        cycle_info = get_test_cycle_info(cycle_id)
        
        target_id_int = case_info["id"]
        items_list = cycle_info.get("testRunItems", {}).get("testRunItems", [])
        
        # 2. Tìm mã mục tiêu trong đợt chạy
        matchedItem = next((item for item in items_list if item.get("$lastTestResult", {}).get("testCase", {}).get("id") == target_id_int), None)
        
        if not matchedItem:
            print(f"WARNING: Case {test_case_id} does not exist in Cycle {cycle_id}. Automatically adding...")
            if add_test_case_to_cycle(cycle_id, test_case_id):
                # Re-fetch info sau khi add
                cycle_info = get_test_cycle_info(cycle_id)
                items_list = cycle_info.get("testRunItems", {}).get("testRunItems", [])
                matchedItem = next((item for item in items_list if item.get("$lastTestResult", {}).get("testCase", {}).get("key") == test_case_id), None)
            
        if not matchedItem:
            print(f"ERROR: Could not find or add Case {test_case_id} to Cycle {cycle_id}.")
            return False

        # 3. Tạo Execution (Bản ghi bắt đầu làm bài)
        exec_payload = {
            "testCaseId": int(target_id_int),
            "testResult": 3, # In Progress
            "testRunId": int(cycle_info["id"]),
            "testRunItemId": int(matchedItem["id"])
        }
        execution_data = create_test_execution(exec_payload)
        
        # 4. Cập nhật kết quả cuối cùng (1=Pass, 2=Fail)
        res_code = 1 if status.upper() == "PASS" else 2
        update_payload = {
            "id": execution_data["id"],
            "testResult": res_code,
            "executionDate": datetime.now().isoformat() + "Z",
            "comment": log if log else "Auto-synced by QC Agent"
        }
        update_execution_status(update_payload)
        return True
    except Exception as e:
        print(f"ERROR: syncing Zephyr execution: {e}")
        return False

def update_test_cycle_status(cycle_id: str, test_case_id: str, status: str, log: str = "", metadata: dict = None, screenshot_path: str = ""):
    """
    Cập nhật trạng thái Test Cycle. (Đã tạm tắt phần sync theo yêu cầu người dùng).
    """
    print(f"🔄 Preparing to update Jira for case {test_case_id} to [{status}]")
    print(f"[INFO] Bỏ qua bước đồng bộ vào Cycle {cycle_id} theo yêu cầu người dùng.")
    # sync_success = sync_and_execute_test_case(cycle_id, test_case_id, status, log)
    sync_success = True # Giả lập thành công để đi tiếp đến phần tạo Bug nếu có

    if not sync_success:
        print(f"ERROR: Failed to sync and execute test case {test_case_id} in cycle {cycle_id}. Bug creation skipped.")
        return False

    # If status is FAIL and metadata is provided, create a bug
    if status.upper() == "FAIL" and metadata:
        payload = format_jira_payload(status, metadata, log, screenshot_path)
        print(f"BUG: Creating Bug on Jira: {payload['fields']['summary']}")
        
        return create_issue(
            summary=payload['fields']['summary'],
            description=payload['fields']['description'],
            issue_type=payload['fields']['issuetype']['name'],
            project_key=payload['fields']['project']['key']
        )
    
    return True

if __name__ == "__main__":
    # --- BƯỚC 2: TẠO THỬ VỚI DỮ LIỆU ĐÃ BIẾT ---
    print("--- Testing create_zephyr_test_case with exact IDs ---")
    new_tc_key = create_zephyr_test_case(
        name=f"Automation TC - {datetime.now().strftime('%H%M')}",
        objective="Dữ liệu tạo từ Agent với ID chuẩn (Status=42, Priority=52)",
        project_key="NCPP"
    )
    print(f"Result Key: {new_tc_key}")

    if new_tc_key:
        print(f"\n--- Thử đọc lại chính Case vừa tạo ({new_tc_key}) ---")
        info = get_test_case_info(new_tc_key)
        print(f"Success! Fetched Key: {info.get('key')}")