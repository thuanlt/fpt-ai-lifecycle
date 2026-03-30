import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page – replace with the actual URL
        await page.goto("https://example.com/login")

        # Generate a username with 256 characters
        long_username = "a" * 256
        # Fill the username field – adjust selector as needed
        await page.fill("#username", long_username)
        # Click the login button – adjust selector as needed
        await page.click("#loginButton")

        # Verify the inline error message appears
        await page.wait_for_selector("text=Username cannot exceed 255 characters.", timeout=5000)
        inline_error = await page.inner_text("text=Username cannot exceed 255 characters.")
        assert inline_error == "Username cannot exceed 255 characters.", "Inline error message mismatch"

        # Verify that no toast error is displayed – adjust selector as needed
        toast_visible = await page.is_visible(".toast")
        assert not toast_visible, "Toast error should not be displayed"

        await browser.close()

asyncio.run(run())