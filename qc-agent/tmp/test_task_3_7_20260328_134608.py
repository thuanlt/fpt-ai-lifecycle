import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://example.com/login")
        await page.fill('input[name="username"]', 'valid_user')
        await page.fill('input[name="password"]', 'valid_password')
        # Ensure "Remember Me" is unchecked
        remember_checkbox = page.locator('input[name="remember"]')
        if await remember_checkbox.is_checked():
            await remember_checkbox.uncheck()
        await page.click('button:has-text("Submit")')
        # Verify authentication and dashboard load
        await page.wait_for_selector('.dashboard')
        welcome = page.locator('text=Welcome')
        await expect(welcome).to_be_visible()
        await browser.close()

asyncio.run(run())