import asyncio
from playwright.async_api import async_playwright

async def test_login_button():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://example.com/login")
        # Locate the login button by its visible text
        login_button = page.locator("button:has-text('Login')")
        assert await login_button.is_visible(), "Login button should be visible"
        await browser.close()

asyncio.run(test_login_button())
