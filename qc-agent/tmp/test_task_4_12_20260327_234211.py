import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://example.com/api"

async def test_login_user_not_found():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Prepare payload with a non-existent username
        payload = {
            "username": "nonexistent_user_12345",
            "password": "anyPassword"
        }

        # Send POST request to /login endpoint
        response = await page.request.post(
            f"{BASE_URL}/login",
            data=payload
        )

        # Assert status code 404
        assert response.status == 404, f"Expected status 404, got {response.status}"

        # Parse JSON response
        json_body = await response.json()

        # Assert error message contains "user not found"
        error_message = json_body.get("error", "")
        assert "user not found" in error_message.lower(), (
            f"Expected error message to contain 'user not found', got '{error_message}'"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login_user_not_found())
