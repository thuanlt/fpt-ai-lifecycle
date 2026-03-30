import asyncio
from playwright.async_api import async_playwright

# Replace with the actual base URL of the Service Catalog API
BASE_URL = "http://localhost:8000"

async def test_unauthorized_service_creation():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium) – required to obtain a request context
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # Prepare request payload (example payload – adjust fields as needed)
        payload = {
            "name": "Test Service",
            "description": "A service created without authentication",
            # Add other required fields here if the API expects them
        }

        # Send POST request without an Authorization header
        response = await request.post(
            f"{BASE_URL}/services",
            data=payload,
            # No headers such as Authorization are added intentionally
        )

        # Assert that the response status code is 401 Unauthorized
        assert response.status == 401, f"Expected status 401, got {response.status}"

        # Optionally, verify the error message in the response body
        try:
            json_body = await response.json()
            error_message = json_body.get("error") or json_body.get("message") or ""
        except Exception:
            # If response is not JSON, fallback to plain text
            error_message = await response.text()

        assert "authentication" in error_message.lower(), (
            "Expected an authentication error message, got: " + error_message
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_unauthorized_service_creation())
