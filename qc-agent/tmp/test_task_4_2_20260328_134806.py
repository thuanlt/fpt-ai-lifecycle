import asyncio
from playwright.async_api import async_playwright, Request, APIResponse

API_URL = "http://localhost:8000/api/login"  # Adjust base URL as needed

async def test_invalid_login():
    async with async_playwright() as p:
        # Create a new API request context (no UI needed)
        request_context = await p.request.new_context()
        payload = {
            "username": "validUser",
            "password": "WrongPass"
        }
        # Send POST request to the login endpoint
        response: APIResponse = await request_context.post(API_URL, data=payload)
        # Verify HTTP status code is 401 Unauthorized
        assert response.status == 401, f"Expected status 401, got {response.status}"
        # Parse response body as JSON (if applicable)
        try:
            resp_json = await response.json()
        except Exception:
            resp_text = await response.text()
            raise AssertionError(f"Response is not valid JSON: {resp_text}")
        # Verify error message content
        expected_error = "Invalid credentials"
        actual_error = resp_json.get("error") or resp_json.get("message")
        assert actual_error == expected_error, f"Expected error message '{expected_error}', got '{actual_error}'"
        print("Test passed: Invalid login correctly returns 401 with appropriate error message.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(test_invalid_login())
