import asyncio
import json
from playwright.async_api import async_playwright

API_URL = "http://localhost:8000/api/login"  # Adjust host/port as needed

async def main():
    async with async_playwright() as p:
        request_context = await p.request.new_context()
        payload = {"password": "ValidPass123"}
        response = await request_context.post(
            API_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        # Verify HTTP status code
        assert response.status == 400, f"Expected 400 Bad Request, got {response.status}"
        # Parse response body (assuming JSON)
        resp_json = await response.json()
        # Look for validation error mentioning missing username
        error_msg = resp_json.get("error") or resp_json.get("message") or ""
        assert "username" in error_msg.lower(), f"Expected validation error for missing username, got: {error_msg}"
        print("Test passed: Missing username returns 400 with appropriate error message.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
