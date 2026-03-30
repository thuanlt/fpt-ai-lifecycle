import asyncio
import json
from playwright.async_api import async_playwright, Request, APIResponse

# Configuration
BASE_URL = "http://localhost"  # Adjust to your application's base URL
USER_ID = "12345"  # Replace with a valid existing user ID for the test

async def run_test():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium) – required to obtain a request context
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # ---------- Step 1: Send DELETE request ----------
        delete_endpoint = f"{BASE_URL}/api/admin/users/{USER_ID}"
        delete_response: APIResponse = await request.delete(delete_endpoint)

        # Expected Result 1: Status code is 200
        assert delete_response.status == 200, f"Expected status 200, got {delete_response.status}"

        # Expected Result 2: Response body contains confirmation message
        delete_body = await delete_response.text()
        try:
            delete_json = json.loads(delete_body)
        except json.JSONDecodeError:
            delete_json = {}
        confirmation_msg = delete_json.get("message", delete_body)
        assert "User deleted successfully" in confirmation_msg, (
            f"Expected confirmation message not found. Received: {confirmation_msg}"
        )

        # ---------- Step 2: Send GET request for the same user ----------
        get_endpoint = f"{BASE_URL}/api/admin/users/{USER_ID}"
        get_response: APIResponse = await request.get(get_endpoint)

        # Expected Result 3: Status code is 404
        assert get_response.status == 404, f"Expected status 404 after deletion, got {get_response.status}"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
