import asyncio
from playwright.async_api import async_playwright, expect

async def test_invalid_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")
        # Step 1: Enter a valid username
        await page.fill('input[name="username"]', 'valid_user')
        # Step 2: Enter an invalid password
        await page.fill('input[name="password"]', 'wrong_password')
        # Step 3: Click the Submit button
        await page.click('button[type="submit"]')
        # Expected Result: Authentication fails and error message is displayed
        error_locator = page.locator('text="Invalid username or password"')
        await expect(error_locator).to_be_visible(timeout=5000)
        assert await error_locator.text_content() == "Invalid username or password"
        await browser.close()

asyncio.run(test_invalid_login())
