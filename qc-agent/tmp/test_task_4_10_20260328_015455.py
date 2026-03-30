import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Create a request context with base URL and authentication header
        request_context = await p.request.new_context(
            base_url="http://api.example.com",  # TODO: replace with actual service catalog base URL
            extra_http_headers={
                "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # TODO: insert a valid token
                "Content-Type": "application/json"
            }
        )

        # Payload for updating the service
        payload = "{\"name\":\"Updated Service\"}"

        # Send PUT request to update service with id 123
        response = await request_context.put("/services/123", data=payload)

        # Validate response status code
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse JSON response body
        json_body = await response.json()

        # Validate that the service name was updated
        assert json_body.get("name") == "Updated Service", "Service name was not updated in response"

        print("PUT /services/123 test passed.")

        # Clean up the request context
        await request_context.dispose()

# Entry point for the async script
if __name__ == "__main__":
    asyncio.run(run())
