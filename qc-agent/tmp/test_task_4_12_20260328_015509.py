import asyncio
from playwright.async_api import async_playwright, APIResponse

# ---------------------------------------------------------------------------
# Configuration – replace these values with your environment specifics
# ---------------------------------------------------------------------------
BASE_URL = "https://api.example.com"  # Base URL of the Service Catalog API
ADMIN_TOKEN = "YOUR_ADMIN_JWT_OR_API_KEY"  # Valid admin authentication token
SERVICE_ID = "123"  # ID of the service to delete (adjust as needed)

async def delete_service(request_context, service_id: str) -> APIResponse:
    """Send a DELETE request to remove a service.

    Args:
        request_context: Playwright APIRequestContext instance.
        service_id: Identifier of the service to delete.

    Returns:
        APIResponse object representing the DELETE response.
    """
    endpoint = f"/services/{service_id}"
    return await request_context.delete(
        endpoint,
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
    )

async def get_service(request_context, service_id: str) -> APIResponse:
    """Send a GET request to retrieve a service.

    Args:
        request_context: Playwright APIRequestContext instance.
        service_id: Identifier of the service to fetch.

    Returns:
        APIResponse object representing the GET response.
    """
    endpoint = f"/services/{service_id}"
    return await request_context.get(
        endpoint,
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
    )

async def main():
    async with async_playwright() as p:
        # Create a request context with the base URL of the API
        request_context = await p.request.new_context(base_url=BASE_URL)

        # ---------------------------------------------------------------
        # Step 1: DELETE the service
        # ---------------------------------------------------------------
        delete_response = await delete_service(request_context, SERVICE_ID)
        print(f"DELETE /services/{SERVICE_ID} → Status: {delete_response.status}")
        # Expected: 204 No Content
        assert delete_response.status == 204, (
            f"Expected status 204 after DELETE, got {delete_response.status}"
        )

        # ---------------------------------------------------------------
        # Step 2: GET the same service to confirm it no longer exists
        # ---------------------------------------------------------------
        get_response = await get_service(request_context, SERVICE_ID)
        print(f"GET /services/{SERVICE_ID} → Status: {get_response.status}")
        # Expected: 404 Not Found
        assert get_response.status == 404, (
            f"Expected status 404 after GET of deleted service, got {get_response.status}"
        )

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
