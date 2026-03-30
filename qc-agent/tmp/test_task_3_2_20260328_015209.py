import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the Service Catalog page
        await page.goto("http://localhost:3000/service-catalog")

        # Step 1: Click the "Create Service" button
        await page.click('text="Create Service"')

        # Verify that the creation modal/dialog appears with the correct title
        modal = page.locator('role=dialog >> text="Create New Service"')
        await expect(modal).to_be_visible()

        # Verify required input fields are present and enabled
        name_input = page.locator('input[name="name"]')
        category_input = page.locator('select[name="category"], input[name="category"]')
        description_input = page.locator('textarea[name="description"]')

        await expect(name_input).to_be_enabled()
        await expect(category_input).to_be_enabled()
        await expect(description_input).to_be_enabled()

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run())
