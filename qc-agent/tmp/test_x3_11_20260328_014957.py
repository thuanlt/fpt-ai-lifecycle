import asyncio
from playwright.async_api import async_playwright

# Configuration
API_BASE_URL = "http://localhost"  # Replace with the actual base URL of the application
CREATE_USER_ENDPOINT = "/api/admin/users"
EXISTING_USERNAME = "testuser"  # Username that is known to already exist in the system
EXPECTED_STATUS = 409
EXPECTED_ERROR_MESSAGE = "Username already exists"

async def main():
    async with async_playwright() as p:
        # Create a request context (no UI needed for API testing)
        request_context = await p.request.new_context()
        url = f"{API_BASE_URL}{CREATE_USER_ENDPOINT}"
        payload = {
            "username": EXISTING_USERNAME,
            "password": "SomeSecurePassword123!",
            "email": "testuser@example.com"
        }
        # Send POST request to create user with an existing username
        response = await request_context.post(url, data=payload)
        # Assert response status code
        assert response.status == EXPECTED_STATUS, (
            f"Expected status {EXPECTED_STATUS}, got {response.status}"
        )
        # Parse response body (assuming JSON)
        try:
            response_json = await response.json()
        except Exception:
            response_text = await response.text()
            raise AssertionError(
                f"Response is not valid JSON. Body: {response_text}"
            )
        # Verify error message in response body
        error_message = response_json.get("error") or response_json.get("message")
        assert error_message is not None, "Error message not found in response body"
        assert EXPECTED_ERROR_MESSAGE in error_message, (
            f"Expected error message to contain '{EXPECTED_ERROR_MESSAGE}', got '{error_message}'"
        )
        print("Test passed: API correctly enforces unique username constraint.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
