import os
import requests
import json

os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'

payload = {
    "instruction": "generate a simple test case for login",
    "cycle_id": "NCPP-C999",
    "project_key": "NCPP",
    "planner_model": "SaoLa-Llama3.1-planner",
    "tester_model": "gpt-oss-120b"
}

try:
    print("Sending POST request to /fast-track (600s timeout)...")
    r = requests.post(
        "http://127.0.0.1:5001/fast-track", 
        json=payload, 
        timeout=600, 
        proxies={"http": None, "https": None}
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success!")
        print("Received valid JSON response.")
    else:
        print(f"Error Body: {r.text}")
except Exception as e:
    print(f"Error: {e}")
