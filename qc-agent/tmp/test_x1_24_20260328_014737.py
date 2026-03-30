import asyncio
import json
from playwright.async_api import async_playwright, Request, APIResponse

BASE_URL = "http://localhost:3000"  # Adjust to the actual API host
USER_ID = "123"  # Replace with a valid user identifier for the test environment

async def main():
    async with async_playwright() as p:
        # Create a new API request context
        request_context = await p.request.new_context()

        # Prepare the payload
        payload = {"firstName": "Anna"}
        headers = {
            "Content-Type": "application/json"
        }

        # Send PATCH request to update user profile
        response: APIResponse = await request_context.patch(
            f"{BASE_URL}/api/users/{USER_ID}",
            data=json.dumps(payload),
            headers=headers
        )

        # Assert response status code
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse and validate response body
        response_json = await response.json()
        assert response_json.get("firstName") == "Anna", (
            f"Expected firstName to be 'Anna', got {response_json.get('firstName')}"
        )

        # Validate ETag header is present and non‑empty
        etag = response.headers.get("etag") or response.headers.get("ETag")
        assert etag, "ETag header is missing or empty in the response"

        print("Test passed: PATCH /api/users/{userId} behaves as expected.")

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
