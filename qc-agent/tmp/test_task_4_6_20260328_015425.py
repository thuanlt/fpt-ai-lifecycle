import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Create an API request context with base URL and authentication header
        request_context = await p.request.new_context(
            base_url="https://example.com",  # <-- replace with actual service catalog base URL
            extra_http_headers={
                "Authorization": "Bearer YOUR_VALID_TOKEN"  # <-- replace with a valid token
            }
        )

        # Payload deliberately omits the required "name" field
        payload = {
            "description": "Test service without name"
            # add any other optional fields here if needed
        }

        # Send POST request to /services endpoint
        response = await request_context.post("/services", data=payload)

        # Verify that the response status code is 400 Bad Request
        assert response.status == 400, f"Expected status 400, got {response.status}"

        # Parse response body (assuming JSON) and check for validation error about 'name'
        try:
            resp_json = await response.json()
        except Exception:
            resp_json = {}
        error_message = resp_json.get("error", "") or resp_json.get("message", "")
        assert "name" in str(error_message).lower(), "Validation error does not indicate missing 'name' field"

        print("✅ POST /services missing required 'name' field – test passed")

        # Clean up the request context
        await request_context.dispose()

# Entry point
if __name__ == "__main__":
    asyncio.run(run())
