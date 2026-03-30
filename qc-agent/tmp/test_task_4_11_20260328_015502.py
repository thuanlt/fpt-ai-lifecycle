import asyncio
from playwright.async_api import async_playwright, APIResponse

# Replace with the actual base URL of the Service Catalog API
BASE_URL = "https://api.example.com"
# Replace with a valid authentication token
AUTH_TOKEN = "YOUR_VALID_TOKEN_HERE"

async def run():
    async with async_playwright() as p:
        # Create a request context with the base URL and authentication header
        request_context = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        # Payload for the update – can be empty or contain dummy data since the service does not exist
        payload = {
            "name": "Updated Service Name",
            "description": "Updated description"
        }

        # Send PUT request to a non‑existent service ID (e.g., 99999)
        response: APIResponse = await request_context.put(
            "/services/99999",
            data=payload
        )

        # Assert that the status code is 404 Not Found
        assert response.status == 404, f"Expected status 404, got {response.status}"
        print("✅ Status code is 404 as expected.")

        # Try to parse the response body as JSON; fall back to text if parsing fails
        try:
            body = await response.json()
            error_message = body.get("error", "") or body.get("message", "")
        except Exception:
            error_message = await response.text()

        # Verify that the error message indicates the service was not found
        assert "service not found" in error_message.lower(), (
            f"Expected error message to contain 'service not found', got: {error_message}"
        )
        print("✅ Error message correctly indicates service not found.")

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(run())
