import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to login page
        await page.goto("https://example.com/login")
        # Wait for page load
        await page.wait_for_load_state('networkidle')
        # Enter username with expired password
        await page.fill("#username", "expired_user")
        await page.fill("#password", "any_password")
        # Click login
        await page.click("#loginButton")
        # Wait for potential prompt
        await page.wait_for_selector("#resetPasswordPrompt", timeout=5000)
        # Assert prompt visible
        assert await page.is_visible("#resetPasswordPrompt")
        # Assert still on login page
        assert page.url == "https://example.com/login"
        print("Test passed: Reset password prompt displayed and remained on login page.")
        await browser.close()

asyncio.run(run())