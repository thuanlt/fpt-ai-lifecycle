import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Create an API request context. Adjust the base URL to point to the Service Catalog API.
        request_context = await p.request.new_context(
            base_url="https://api.example.com",
            extra_http_headers={
                "Authorization": "Bearer NON_ADMIN_TOKEN"  # Token for a user without the 'admin' role
            }
        )
        # Send POST request to /services (empty payload for this example)
        response = await request_context.post("/services", json={})
        # Verify that the response status code is 403 Forbidden
        assert response.status == 403, f"Expected status 403, got {response.status}"
        # Parse response body (assuming JSON) and check error message
        try:
            body = await response.json()
        except Exception:
            body = {}
        error_message = str(body.get("error", "")).lower()
        assert "insufficient permissions" in error_message, (
            f"Expected error about insufficient permissions, got: {error_message}"
        )
        print("Test passed: Received 403 Forbidden with appropriate error message.")
        await request_context.dispose()

asyncio.run(run())
