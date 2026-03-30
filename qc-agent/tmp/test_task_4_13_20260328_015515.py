import asyncio
from playwright.async_api import async_playwright, APIResponse

# Replace with the actual base URL of the Service Catalog API
BASE_URL = "https://api.example.com"
# Replace with a valid token for a non‑admin user
NON_ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

async def test_delete_service_without_permission():
    async with async_playwright() as p:
        # Create a request context (no UI needed for API testing)
        request_context = await p.request.new_context(
            base_url=BASE_URL,
            extra_http_headers={
                "Authorization": f"Bearer {NON_ADMIN_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        service_id = "123"  # Example service ID to attempt deletion
        endpoint = f"/services/{service_id}"

        # Send DELETE request
        response: APIResponse = await request_context.delete(endpoint)

        # Assert HTTP status code is 403 Forbidden
        assert response.status == 403, f"Expected status 403, got {response.status}"

        # Parse JSON body (if any) and verify error message about insufficient permissions
        try:
            json_body = await response.json()
        except Exception:
            json_body = {}

        error_message = json_body.get("error") or json_body.get("message") or ""
        assert "insufficient permission" in error_message.lower() or "forbidden" in error_message.lower(), (
            f"Expected error message about insufficient permissions, got: '{error_message}'"
        )

        print("Test passed: DELETE without permission returns 403 and appropriate error message.")

        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(test_delete_service_without_permission())
