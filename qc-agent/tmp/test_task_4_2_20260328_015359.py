import asyncio
from playwright.async_api import async_playwright

# Replace with the actual base URL of the Service Catalog API
BASE_URL = "http://example.com"

async def test_get_services_unauthorized():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium) – required to obtain a request context
        browser = await p.chromium.launch()
        context = await browser.new_context()
        # Use the APIRequestContext from the browser context
        request = context.request
        # Perform GET request without any authentication headers
        response = await request.get(f"{BASE_URL}/services")
        # Assert that the response status code is 401 Unauthorized
        assert response.status == 401, f"Expected status 401, got {response.status}"
        # Optionally, verify the error message in the response body
        try:
            json_body = await response.json()
            error_message = json_body.get("error") or json_body.get("message")
        except Exception:
            # If response is not JSON, fallback to plain text
            error_message = await response.text()
        assert error_message, "Error message should be present in the response"
        # Example check for a typical unauthorized error phrase (customize as needed)
        assert "unauthorized" in error_message.lower(), f"Unexpected error message: {error_message}"
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_get_services_unauthorized())
