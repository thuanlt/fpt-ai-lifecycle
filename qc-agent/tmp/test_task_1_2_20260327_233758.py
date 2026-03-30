import asyncio
from playwright.async_api import async_playwright, expect

async def test_login_default_state():
    """Verify that the login page shows empty input fields and a disabled login button on load."""
    async with async_playwright() as p:
        # Launch browser (headless can be set to True if desired)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Replace with the actual login page URL
        await page.goto("https://example.com/login")

        # Locators for username, password and login button
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        login_button = page.locator('button[type="submit"]')

        # 1. Verify default state of input fields
        assert await username_input.input_value() == "", "Username field should be empty on load"
        assert await password_input.input_value() == "", "Password field should be empty on load"

        # 2. Verify login button is disabled initially
        assert await login_button.is_disabled(), "Login button should be disabled when inputs are empty"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login_default_state())
