import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Fill in the username/email field (assuming it is required for the test)
        await page.fill('input[name="username"]', 'testuser')
        # Leave the password field empty

        # Click the login button
        await page.click('button[type="submit"]')

        # Verify inline error message for password
        error_locator = page.locator('.error-password')
        await expect(error_locator).to_be_visible(timeout=5000)
        error_text = await error_locator.text_content()
        assert error_text.strip() == "Password is required.", f"Expected 'Password is required.', got '{error_text}'"

        # Verify that no toast notification appears
        toast_locator = page.locator('.toast')
        assert not await toast_locator.is_visible(), "Toast should not be visible"

        await browser.close()

asyncio.run(run())