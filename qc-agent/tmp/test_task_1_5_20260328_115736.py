import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Navigate to the Service Management page (adjust URL as needed)
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")  # <-- replace with real login URL
        # If authentication is required, add login steps here.
        await page.goto("https://example.com/service-management")

        # ------------------------------------------------------------
        # 1. Fill mandatory fields (Name, Version) with valid data
        #    and optional fields as desired, then click Save
        # ------------------------------------------------------------
        await page.fill('input[name="serviceName"]', 'Test Service')
        await page.fill('input[name="serviceVersion"]', '1.0.0')
        # Optional field example
        await page.fill('textarea[name="serviceDescription"]', 'Automated test service')
        await page.click('button:has-text("Save")')

        # ------------------------------------------------------------
        # 2. Verify creation success message
        # ------------------------------------------------------------
        await page.wait_for_selector('text=Service is created successfully')

        # ------------------------------------------------------------
        # 3. Verify the new service appears in the service list with status "Draft"
        # ------------------------------------------------------------
        # Wait for the service row to be present in the table/list
        service_row = page.locator('tr:has-text("Test Service")')
        await expect(service_row).to_be_visible()
        # Check the status column (assumes a CSS class or position for status)
        await expect(service_row.locator('td.status')).to_have_text('Draft')

        # ------------------------------------------------------------
        # 4. Verify the service record details are correct
        # ------------------------------------------------------------
        await service_row.click()  # Open detail view (adjust if a different action is required)
        await expect(page.locator('input[name="serviceName"]')).to_have_value('Test Service')
        await expect(page.locator('input[name="serviceVersion"]')).to_have_value('1.0.0')
        await expect(page.locator('textarea[name="serviceDescription"]')).to_have_text('Automated test service')

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run())