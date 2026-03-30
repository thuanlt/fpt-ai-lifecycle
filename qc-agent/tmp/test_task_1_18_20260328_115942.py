import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8000"  # Adjust to the actual service URL
SERVICE_ID = "12345"               # Replace with a valid service identifier
NEW_DESCRIPTION = "Updated service description"

async def main():
    async with async_playwright() as p:
        # Launch a headless browser (required to obtain a request context)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # ------------------------------------------------------------
        # Step 1: Send HTTP PUT to /api/services/{id} with modified description
        # ------------------------------------------------------------
        put_response = await request.put(
            f"{BASE_URL}/api/services/{SERVICE_ID}",
            data={"description": NEW_DESCRIPTION},
            headers={"Content-Type": "application/json"}
        )
        # => Response status 200 OK
        assert put_response.status == 200, f"Expected 200 OK, got {put_response.status}"
        put_body = await put_response.json()
        # => Updated fields are persisted and reflected in GET response
        assert put_body.get("description") == NEW_DESCRIPTION, "PUT response does not contain updated description"

        # ------------------------------------------------------------
        # Step 2: Verify persistence with a GET request
        # ------------------------------------------------------------
        get_response = await request.get(f"{BASE_URL}/api/services/{SERVICE_ID}")
        assert get_response.status == 200, f"GET after update failed with status {get_response.status}"
        get_body = await get_response.json()
        assert get_body.get("description") == NEW_DESCRIPTION, "Updated description not persisted in GET response"

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
