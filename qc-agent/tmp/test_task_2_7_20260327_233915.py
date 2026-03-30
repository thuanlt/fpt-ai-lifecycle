import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Generate a password with 129 characters
        long_password = "a" * 129

        # Fill the password field and click the login button
        await page.fill("#password", long_password)
        await page.click("#loginButton")

        # Verify the inline error message appears
        error_locator = page.locator(".error-message")
        await expect(error_locator).to_have_text(
            "Password cannot exceed 128 characters.", timeout=5000
        )

        # Verify that no toast notification is displayed
        toast_locator = page.locator(".toast")
        assert not await toast_locator.is_visible(), "Toast should not be displayed"

        await browser.close()

asyncio.run(run())