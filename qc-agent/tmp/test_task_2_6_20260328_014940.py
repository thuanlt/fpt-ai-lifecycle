import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Catalog Management screen
        # TODO: Replace with the actual URL of the Service Catalog page
        await page.goto("https://example.com/service-catalog")

        # ---------- Test Step 1: Enter a 21‑character Service Code ----------
        long_service_code = "A" * 21  # 21 characters
        # TODO: Replace the selector with the actual input field for Service Code
        await page.fill('input[name="serviceCode"]', long_service_code)

        # ---------- Test Step 2: Attempt to save ----------
        # TODO: Replace the selector with the actual Save button
        await page.click('button#save')

        # ---------- Expected Result: Validation error is displayed ----------
        # The error message should be exactly as defined in the requirement
        error_message = "Service Code cannot exceed 20 characters"
        error_locator = page.locator(f'text={error_message}')
        await expect(error_locator).to_be_visible()

        # Optional: Verify that the form is still present (save was blocked)
        # TODO: Adjust selector if needed
        form_locator = page.locator('form#serviceCatalogForm')
        await expect(form_locator).to_be_visible()

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run())
