import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Prepare a username that exceeds the maximum allowed length (256 characters)
        long_username = "a" * 256

        # Fill in the login form
        await page.fill('input[name="username"]', long_username)
        await page.fill('input[name="password"]', "AnyPassword123")

        # Submit the form
        await page.click('button[type="submit"]')

        # Verify the inline validation message is displayed
        validation_message = page.locator('text=Username exceeds maximum length')
        await expect(validation_message).to_be_visible()

        # Clean up
        await browser.close()

asyncio.run(run())
