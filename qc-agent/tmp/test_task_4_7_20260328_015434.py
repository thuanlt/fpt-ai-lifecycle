import asyncio
from playwright.async_api import async_playwright

# Replace with the actual base URL of the Service Catalog API
BASE_URL = "https://api.example.com"
# Replace with a valid authentication token for the API
AUTH_TOKEN = "YOUR_VALID_TOKEN"

async def test_post_service_name_exceeds_max_length():
    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(base_url=BASE_URL)

        # Build a payload where the "name" field exceeds the 255‑character limit
        long_name = "a" * 256  # 256 characters
        payload = {
            "name": long_name,
            # Add other required fields for the /services endpoint if any
            # "description": "Sample service",
        }

        # Send POST request with a valid Bearer token
        response = await request_context.post(
            "/services",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            data=payload,
        )

        # Verify that the API returns a 400 Bad Request status code
        assert response.status == 400, f"Expected status 400, got {response.status}"

        # Attempt to parse the response body as JSON
        try:
            resp_json = await response.json()
        except Exception as e:
            raise AssertionError(f"Response is not valid JSON: {e}")

        # Validate that the error message indicates the name length issue
        # The exact structure depends on the API; adjust the keys as needed.
        error_message = resp_json.get("error") or resp_json.get("message") or ""
        assert "name" in error_message.lower() and "length" in error_message.lower(), (
            "Expected validation error about name length, got: " + str(error_message)
        )

        print("✅ Test passed: Exceeding max length for 'name' returns 400 with appropriate validation error.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(test_post_service_name_exceeds_max_length())
