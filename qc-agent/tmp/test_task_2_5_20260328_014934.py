import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Navigate to the Service Catalog Management page
        # Replace the URL below with the actual environment URL
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-catalog")

        # ------------------------------------------------------------
        # Fill in all mandatory fields **except** Service Code
        # Adjust the selectors to match the real application
        # ------------------------------------------------------------
        await page.fill('input[name="serviceName"]', 'Test Service')
        await page.fill('textarea[name="description"]', 'Test description')
        # Service Code is intentionally left empty to trigger validation

        # ------------------------------------------------------------
        # Click the Save button
        # ------------------------------------------------------------
        await page.click('button:has-text("Save")')

        # ------------------------------------------------------------
        # Verify validation error for empty Service Code
        # ------------------------------------------------------------
        error_message = page.locator('text=Service Code is required')
        await expect(error_message).to_be_visible()

        # ------------------------------------------------------------
        # Ensure that the form was not submitted (still on the same page)
        # Adjust the URL check as needed for your application routing
        # ------------------------------------------------------------
        await expect(page).to_have_url("https://example.com/service-catalog")

        await browser.close()

asyncio.run(run())
