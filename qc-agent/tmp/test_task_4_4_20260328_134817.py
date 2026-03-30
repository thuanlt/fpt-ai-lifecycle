import asyncio
import json
from playwright.async_api import async_playwright, APIResponse

async def main():
    # Initialize Playwright and create a request context
    async with async_playwright() as p:
        # Adjust the base URL to point to the target environment
        request_context = await p.request.new_context(base_url="http://localhost:8000")

        # Prepare the payload with the missing password field
        payload = {"username": "validUser"}
        headers = {"Content-Type": "application/json"}

        # Send POST request to the login endpoint
        response: APIResponse = await request_context.post(
            "/api/login",
            data=json.dumps(payload),
            headers=headers
        )

        # Validate HTTP status code
        assert response.status == 400, f"Expected status 400, got {response.status}"

        # Validate response body contains the expected validation error
        try:
            resp_json = await response.json()
            error_message = resp_json.get("error", "")
        except Exception:
            # Fallback to plain text if JSON parsing fails
            error_message = await response.text()

        assert "missing password" in error_message.lower(), (
            f"Expected validation error for missing password, got: {error_message}"
        )

        print("Test passed: Login fails with missing password (400 Bad Request).")

if __name__ == "__main__":
    asyncio.run(main())
