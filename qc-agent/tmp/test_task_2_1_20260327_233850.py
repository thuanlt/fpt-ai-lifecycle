import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Ensure the username/email field is empty
        await page.fill("#username", "")

        # Click the login button
        await page.click("#loginButton")

        # Wait for the inline error message to appear
        await page.wait_for_selector(".error-message", state="visible", timeout=5000)
        error_text = await page.text_content(".error-message")
        assert error_text.strip() == "Username is required.", f"Unexpected error text: {error_text}"

        # Verify that no toast notification is displayed
        toast_visible = await page.is_visible(".toast")
        assert not toast_visible, "Toast should not be displayed"

        print("Test passed.")

        await context.close()
        await browser.close()

asyncio.run(main())