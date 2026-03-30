import asyncio
from playwright.async_api import async_playwright, APIResponse

# Replace with the actual base URL of the Service Catalog API
BASE_URL = "https://api.example.com"
# Replace with a valid admin token for authentication
ADMIN_TOKEN = "YOUR_ADMIN_TOKEN_HERE"

async def run():
    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        # Send DELETE request for a non‑existent service (ID: 99999)
        response: APIResponse = await request_context.delete("/services/99999")

        # Validate the HTTP status code
        assert response.status == 404, f"Expected status 404, got {response.status}"

        # Parse the JSON body (if any) and validate the error message
        try:
            json_body = await response.json()
        except Exception:
            json_body = {}
        error_message = json_body.get("error") or json_body.get("message") or ""
        assert "service not found" in error_message.lower(), (
            f"Expected error message indicating service not found, got: '{error_message}'"
        )

        print("Test passed: DELETE non‑existent service returned 404 with appropriate error message.")

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(run())
