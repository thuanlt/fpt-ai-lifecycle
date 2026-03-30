import asyncio
from playwright.async_api import async_playwright, expect

async def run_test():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # TODO: Replace the URL below with the actual location of the
        #       "Create User" form in the application under test.
        # ------------------------------------------------------------
        await page.goto("https://example.com/create-user")

        # Fill in all required fields **except** Username (leave it empty)
        await page.fill('input[name="email"]', "test@example.com")
        await page.fill('input[name="password"]', "Password123!")
        # Username field is intentionally left blank

        # Submit the form
        await page.click('button:has-text("Save")')

        # -----------------------------------------------------------------
        # Verify the inline validation error for the Username field appears.
        # The selector assumes the error text is rendered directly on the page.
        # Adjust the locator if the application uses a specific element ID or
        # class for field errors (e.g., '#username-error').
        # -----------------------------------------------------------------
        username_error = page.locator('text=Username is required')
        await expect(username_error).to_be_visible()

        # Ensure the form remains open – the Save button should still be visible.
        await expect(page.locator('button:has-text("Save")')).to_be_visible()

        await browser.close()

asyncio.run(run_test())
