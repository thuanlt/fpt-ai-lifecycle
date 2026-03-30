import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://api.example.com"
ENDPOINT = "/login"

async def main():
    async with async_playwright() as p:
        # Create a new request context
        client = await p.request.new_context()

        # Payload with only password field
        payload = {
            "password": "TestPass123"
        }

        # Send POST request to the login endpoint
        response = await client.post(f"{BASE_URL}{ENDPOINT}", data=payload)

        # Assert status code is 400
        assert response.status == 400, f"Expected status 400, got {response.status}"

        # Parse JSON response
        try:
            resp_json = await response.json()
        except Exception as e:
            raise AssertionError(f"Response is not valid JSON: {e}")

        # Assert error message
        expected_error = "username is required"
        actual_error = resp_json.get("error") or resp_json.get("message")
        assert actual_error == expected_error, (
            f"Expected error message '{expected_error}', got '{actual_error}'"
        )

        print("Test passed: Missing username field handled correctly.")

if __name__ == "__main__":
    asyncio.run(main())