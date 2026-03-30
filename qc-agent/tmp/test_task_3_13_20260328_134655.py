import asyncio
from playwright.async_api import async_playwright, expect

async def test_invalid_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")
        # Fill in non‑existent username and any password
        await page.fill('input[name="username"]', 'nonexistent_user')
        await page.fill('input[name="password"]', 'anyPassword123')
        # Click the submit button (adjust selector if needed)
        await page.click('button[type="submit"]')
        # Verify authentication fails and error message is displayed
        error_message = page.locator('text=Invalid username or password')
        await expect(error_message).to_be_visible()
        # Optionally, assert that the user is not logged in
        # await expect(page).not_to_have_url("**/dashboard")
        await browser.close()

asyncio.run(test_invalid_login())