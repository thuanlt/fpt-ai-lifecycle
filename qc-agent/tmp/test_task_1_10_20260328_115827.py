import asyncio
from playwright.async_api import async_playwright, expect

async def run_test():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Navigate to the Service Management page
        # ------------------------------------------------------------
        await page.goto("http://your-app-url.com/service-management")

        # ------------------------------------------------------------
        # 1. Create a service with version "1.0.0"
        # ------------------------------------------------------------
        await page.fill('input[name="serviceName"]', 'Test Service')
        await page.fill('input[name="serviceVersion"]', '1.0.0')
        await page.click('button#create-service')

        # Verify that the service was created (adjust selector to actual UI feedback)
        await expect(page.locator('text=Service created successfully')).to_be_visible()

        # ------------------------------------------------------------
        # 2. Attempt to create another service with the same name and version "1.0.0"
        # ------------------------------------------------------------
        # Clear previous inputs if needed
        await page.fill('input[name="serviceName"]', '')
        await page.fill('input[name="serviceVersion"]', '')
        await page.fill('input[name="serviceName"]', 'Test Service')
        await page.fill('input[name="serviceVersion"]', '1.0.0')
        await page.click('button#create-service')

        # Verify validation error appears
        await expect(page.locator('text=Version already exists for this service')).to_be_visible()

        # Ensure the duplicate service was NOT added to the list
        # (Assuming services are displayed in a table with id "services")
        rows = await page.locator('table#services tbody tr').count()
        if rows != 1:
            raise AssertionError('Duplicate service was created; expected only one entry in the list')

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run_test())
