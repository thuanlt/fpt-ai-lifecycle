import asyncio
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Configuration – replace the placeholders with real values for your environment
# ---------------------------------------------------------------------------
BASE_URL = "https://api.example.com"  # TODO: set the actual Service Catalog base URL
AUTH_TOKEN = "YOUR_VALID_AUTH_TOKEN"  # TODO: set a valid authentication token

async def test_get_services():
    """Validate GET /services returns 200 and an array of service objects."""
    async with async_playwright() as p:
        # Create a request context with the base URL and auth header
        request = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
        )
        # Send the GET request
        response = await request.get("/services")

        # ---- Expected Result 1 ------------------------------------------------
        # => Response status code 200 OK
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # ---- Expected Result 2 ------------------------------------------------
        # => Response body contains an array of service objects
        json_body = await response.json()
        assert isinstance(json_body, list), (
            f"Response body is not an array. Received: {json_body}"
        )

        print("✅ GET /services passed: status 200 and response is an array.")
        await request.dispose()

# Entry point for running the async test directly
if __name__ == "__main__":
    asyncio.run(test_get_services())
