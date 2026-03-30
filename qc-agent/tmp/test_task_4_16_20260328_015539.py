import asyncio
from playwright.async_api import async_playwright

async def main():
    # TODO: Replace with the actual base URL of the Service Catalog API
    base_url = "https://api.example.com"
    # TODO: Insert a valid authentication token
    token = "YOUR_VALID_TOKEN"

    async with async_playwright() as p:
        # Launch a headless browser (required to obtain a request context)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # Send GET request to /services endpoint with a valid Authorization header
        response = await request.get(
            f"{base_url}/services",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify that the simulated backend failure returns HTTP 500
        assert response.status == 500, f"Expected status 500, got {response.status}"

        # Attempt to parse the response body as JSON (adjust if the API returns plain text)
        try:
            body = await response.json()
        except Exception:
            body = await response.text()

        # Extract the error message – adapt the key according to the API contract
        if isinstance(body, dict):
            error_message = body.get("message", "")
        else:
            error_message = body

        # Validate that the error message is generic and does not expose a stack trace
        assert "error" in error_message.lower(), "Error message does not appear to be generic"
        assert "stack" not in error_message.lower(), "Stack trace found in error message"

        await browser.close()

asyncio.run(main())
