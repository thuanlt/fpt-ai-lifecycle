import asyncio
from playwright.async_api import async_playwright, expect

async def test_login_username_only():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")
        # Enter a valid username
        await page.fill('input[name="username"]', "validUser")
        # Ensure password field is left empty
        await page.fill('input[name="password"]', "")
        # Click the submit/login button
        await page.click('button[type="submit"]')
        # Verify the inline validation message for missing password
        password_error = page.locator('text=Password is required')
        await expect(password_error).to_be_visible()
        await browser.close()

asyncio.run(test_login_username_only())