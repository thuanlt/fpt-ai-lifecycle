import asyncio
from playwright.async_api import async_playwright

# Replace with the actual Login API endpoint
LOGIN_URL = "https://example.com/api/login"

async def main():
    async with async_playwright() as p:
        # Create a new request context
        context = await p.chromium.launch()
        # Send a malformed request to trigger a server error
        # For example, missing required fields or sending an invalid JSON structure
        malformed_payload = {
            "username": "test_user",
            # Intentionally omit the password field or provide an invalid type
            "password": 12345  # should be a string
        }
        response = await context.request.post(
            LOGIN_URL,
            data=malformed_payload,
            headers={"Content-Type": "application/json"}
        )

        # Assert the response status code is 500
        assert response.status == 500, f"Expected status 500, got {response.status}"

        # Assert the response body contains the expected error message
        body_text = await response.text()
        assert "internal server error" in body_text.lower(), (
            f"Expected error message not found in response body: {body_text}"
        )

        print("Test passed: Received 500 Internal Server Error with expected message.")

        await context.close()

if __name__ == "__main__":
    asyncio.run(main())