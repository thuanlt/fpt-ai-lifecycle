import asyncio
import json
from playwright.async_api import async_playwright, APIResponse

BASE_URL = "http://localhost:8000"  # Adjust to your service registry host

async def test_create_service_instance():
    payload = {
        "name": "AuthSvc",
        "type": "Authentication",
        "version": "1.0.0"
    }
    async with async_playwright() as p:
        # Create a new API request context
        request_context = await p.request.new_context(base_url=BASE_URL)
        # Send POST request to create a new instance
        response: APIResponse = await request_context.post("/api/instances", data=json.dumps(payload), headers={"Content-Type": "application/json"})
        # Assert response status code
        assert response.status == 201, f"Expected status 201, got {response.status}"
        # Parse response body
        resp_json = await response.json()
        # Verify that response contains an ID and echoes the supplied details
        assert "id" in resp_json, "Response JSON does not contain 'id' field"
        assert resp_json.get("name") == payload["name"], f"Name mismatch: expected {payload['name']}, got {resp_json.get('name')}"
        assert resp_json.get("type") == payload["type"], f"Type mismatch: expected {payload['type']}, got {resp_json.get('type')}"
        assert resp_json.get("version") == payload["version"], f"Version mismatch: expected {payload['version']}, got {resp_json.get('version')}"
        print("Test passed: Service instance created successfully with ID", resp_json["id"])
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(test_create_service_instance())
