import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://example.com/login")  # Replace with actual login URL

        # Enter an email that already exists in the system
        await page.fill("#email", "existing_user@example.com")
        # Enter any password (required field)
        await page.fill("#password", "Password123!")
        # Click the login button
        await page.click("#loginButton")

        # Verify inline error message
        inline_error_selector = ".inline-error"
        await expect(page.locator(inline_error_selector)).to_be_visible()
        error_text = await page.locator(inline_error_selector).inner_text()
        assert error_text.strip() == "User already exists.", f"Unexpected error text: {error_text}"

        # Verify that no toast error is displayed
        toast_selector = ".toast"
        # Wait briefly to allow any toast to appear if it were going to
        await page.wait_for_timeout(2000)
        toast_visible = await page.is_visible(toast_selector)
        assert not toast_visible, "Toast error should not be displayed"

        print("Test passed.")
        await context.close()
        await browser.close()

asyncio.run(run())