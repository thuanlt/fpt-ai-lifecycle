import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the Service Catalog Management screen
        await page.goto("https://your-application-url.com/service-catalog")

        # OPTIONAL: Perform any navigation steps required to reach the form
        # e.g., await page.click('text=Service Catalog')

        # Construct an email longer than 254 characters
        # 250 "a" characters + "@example.com" (12 chars) = 262 characters > 254
        long_email = "a" * 250 + "@example.com"

        # Fill the Owner Email field – adjust the selector to match the real field
        await page.fill('input[name="ownerEmail"]', long_email)

        # Click the Save button – adjust the selector as needed
        await page.click('button#save')

        # Verify that the appropriate validation error is displayed
        error_message = "Email exceeds maximum length of 254 characters"
        error_locator = page.locator(f'text={error_message}')
        assert await error_locator.is_visible(), "Expected max‑length error was not shown"

        # Verify that the save operation was blocked (form remains open)
        # One simple check is that the Save button is still enabled or the URL has not changed
        # Adjust according to the application's behaviour
        assert await page.is_visible('button#save'), "Save button should remain visible after validation failure"

        await browser.close()

asyncio.run(run())
