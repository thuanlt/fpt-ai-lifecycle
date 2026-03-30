import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'
import requests

try:
    # Explicitly disable proxies for this request
    r = requests.get("http://127.0.0.1:5001/info", timeout=5, proxies={"http": None, "https": None})
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text}")
except Exception as e:
    print(f"Error: {e}")
