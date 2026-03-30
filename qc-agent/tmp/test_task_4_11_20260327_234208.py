import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://example.com"  # Replace with the actual API base URL

async def test_login_incorrect_password():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        payload = {
            "username": "valid_user",
            "password": "wrong_password"
        }

        response = await page.request.post(f"{BASE_URL}/login", data=payload)

        # Assert status code
        assert response.status == 401, f"Expected status 401, got {response.status}"

        # Assert response body contains the expected error message
        body = await response.json()
        assert "error" in body, "Response body missing 'error' key"
        assert body["error"] == "invalid credentials", f"Unexpected error message: {body['error']}"

        await browser.close()

asyncio.run(test_login_incorrect_password())