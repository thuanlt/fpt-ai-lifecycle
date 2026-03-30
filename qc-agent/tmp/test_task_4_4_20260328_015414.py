import asyncio
from playwright.async_api import async_playwright, APIResponse

# Configuration
BASE_URL = "https://api.example.com"  # Replace with the actual base URL of the Service Catalog API
TOKEN = "YOUR_VALID_TOKEN_HERE"      # Replace with a valid authentication token
SERVICE_ID_NOT_FOUND = "99999"

async def test_get_service_not_found():
    async with async_playwright() as p:
        # Launch a headless browser (required to obtain a request context)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # Build the request URL
        url = f"{BASE_URL}/services/{SERVICE_ID_NOT_FOUND}"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json",
        }

        # Send GET request
        response: APIResponse = await request.get(url, headers=headers)

        # Validate response status code
        assert response.status == 404, f"Expected status 404, got {response.status}"

        # Validate error message in response body
        try:
            json_body = await response.json()
        except Exception:
            json_body = {}
        error_message = json_body.get("error") or json_body.get("message") or ""
        assert "service not found" in error_message.lower(), (
            f"Expected error message indicating service not found, got: '{error_message}'"
        )

        print("Test passed: GET /services/{id} returns 404 with appropriate error message when service does not exist.")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_get_service_not_found())
