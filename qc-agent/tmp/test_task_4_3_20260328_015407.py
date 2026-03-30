import asyncio
from playwright.async_api import async_playwright, Request, APIResponse

# Configuration
BASE_URL = "https://api.example.com"  # Replace with the actual base URL of the Service Catalog API
TOKEN = "YOUR_VALID_TOKEN_HERE"      # Replace with a valid authentication token
SERVICE_ID = 123                       # The ID of the service that is known to exist

async def main():
    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "application/json",
            },
        )

        # Send GET request to retrieve the specific service
        response: APIResponse = await request_context.get(f"/services/{SERVICE_ID}")

        # Assert the HTTP status code is 200 OK
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse the JSON response body
        response_json = await response.json()

        # Verify that the response contains a service object with the correct ID
        assert isinstance(response_json, dict), "Response JSON is not an object"
        assert response_json.get("id") == SERVICE_ID, (
            f"Expected service id {SERVICE_ID} in response, got {response_json.get('id')}"
        )

        print("Test passed: GET /services/{id} returned 200 and correct service object.")

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
