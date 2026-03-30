import asyncio
from playwright.async_api import async_playwright

# Adjust BASE_URL to point to the environment under test
BASE_URL = "http://localhost:8000"  # <-- replace with actual host

async def main():
    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(base_url=BASE_URL)

        # TODO: Provide a valid service ID that exists and has no dependent resources
        service_id = "YOUR_DELETABLE_SERVICE_ID"

        # 1. Send HTTP DELETE to /api/services/{id} for a deletable service
        delete_response = await request_context.delete(f"/api/services/{service_id}")
        # - => Response status 204 No Content
        assert delete_response.status == 204, f"Expected status 204, got {delete_response.status}"
        print("✅ DELETE returned 204 No Content")

        # => Subsequent GET for that ID returns 404 Not Found
        get_response = await request_context.get(f"/api/services/{service_id}")
        assert get_response.status == 404, f"Expected status 404, got {get_response.status}"
        print("✅ GET after DELETE returned 404 Not Found")

        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
