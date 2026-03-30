import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page (replace with the actual URL)
        await page.goto("https://example.com/login")

        # Fill in a valid username/email
        await page.fill('input[name="email"]', 'test@example.com')

        # Enter an invalid password (less than 8 characters, missing required character types)
        await page.fill('input[name="password"]', 'short')

        # Submit the form
        await page.click('button[type="submit"]')

        # Verify the inline error message appears
        await page.wait_for_selector('.error-message', state='visible')
        error_text = await page.inner_text('.error-message')
        assert error_text == "Password does not meet complexity requirements.", f"Unexpected error message: {error_text}"

        # Verify that no toast notification is displayed
        toast_visible = await page.is_visible('.toast')
        assert not toast_visible, "Toast notification should not be visible for this validation error."

        print("Test passed")

        await context.close()
        await browser.close()

asyncio.run(main())