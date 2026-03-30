import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://example.com"  # Replace with the actual API base URL

async def test_missing_password():
    async with async_playwright() as p:
        # Create a new request context
        client = await p.request.new_context()

        # Prepare payload with only the username field
        payload = {
            "username": "testuser"
        }

        # Send POST request to the /login endpoint
        response = await client.post(f"{BASE_URL}/login", data=payload)

        # Assert that the status code is 400
        assert response.status == 400, f"Expected status 400, got {response.status}"

        # Parse the response body as JSON
        response_json = await response.json()

        # Assert that the error message contains "password is required"
        error_message = response_json.get("error", "")
        assert "password is required" in error_message, (
            f"Expected error message to contain 'password is required', got '{error_message}'"
        )

        print("Test passed: Missing password field correctly returns 400 with appropriate error message.")

if __name__ == "__main__":
    asyncio.run(test_missing_password())