import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Enter password with disallowed characters
        await page.fill("#password", "<'>")
        # Click the login button
        await page.click("#loginButton")

        # Verify inline error message
        inline_error_selector = ".inline-error"
        await page.wait_for_selector(inline_error_selector, state="visible", timeout=5000)
        error_text = await page.text_content(inline_error_selector)
        assert error_text.strip() == "Password contains invalid characters.", f"Unexpected error text: {error_text}"

        # Verify that no toast error is displayed
        toast_selector = ".toast"
        toast_visible = await page.is_visible(toast_selector)
        assert not toast_visible, "Toast error should not be displayed"

        await browser.close()

asyncio.run(run())