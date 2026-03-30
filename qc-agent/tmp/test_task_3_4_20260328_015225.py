import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the Service Catalog application
        await page.goto("https://example.com/service-catalog")

        # 1. Open the "Create New Service" form
        await page.click('text="Create New Service"')
        await page.wait_for_selector('form#create-service-form')

        # 2. Enter a name consisting of 256 characters, select a valid category, fill description
        long_name = "A" * 256
        await page.fill('input[name="serviceName"]', long_name)
        # Adjust the selector/value according to the actual category field implementation
        await page.select_option('select[name="category"]', label="IT Services")
        await page.fill('textarea[name="description"]', "Test description for long name validation")

        # 3. Click "Save"
        await page.click('button:has-text("Save")')

        # Expected validation error for name length
        await page.wait_for_selector('text="Name cannot exceed 255 characters"', timeout=5000)

        # Verify that the service is not persisted (still on the create form)
        assert await page.is_visible('form#create-service-form'), "Form should remain visible after validation error"

        await browser.close()

asyncio.run(run())
