import asyncio
import json
from playwright.async_api import async_playwright, Request, APIResponse

# Configuration placeholders – replace with actual values
BASE_URL = "https://your-api-domain.com"  # Base URL of the Service Catalog API
TOKEN = "YOUR_ACCESS_TOKEN"  # Bearer token with sufficient permissions

payload = {
    "name": "New Service",
    "description": "Desc",
    "category": "IT"
}

async def main():
    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            }
        )

        # Send POST request to create a new service
        response: APIResponse = await request_context.post(
            "/services",
            data=json.dumps(payload)
        )

        # Assert HTTP status code is 201 Created
        assert response.status == 201, f"Expected status 201, got {response.status}"

        # Parse response body as JSON
        response_json = await response.json()

        # Verify the response contains an assigned id for the created service
        assert "id" in response_json, "Response JSON does not contain 'id' field"
        assert response_json["id"], "The 'id' field is empty"

        print("Test passed: Service created with ID", response_json["id"])

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
