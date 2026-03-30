import asyncio
from playwright.async_api import async_playwright, expect

async def test_activate_service_instance():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the Service Registry page
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-registry")

        # ------------------------------------------------------------
        # 2. Create a new instance "BillingSvc" with status "Inactive"
        # ------------------------------------------------------------
        # Click the button that opens the "Create Instance" dialog/form
        await page.click('button#create-instance')

        # Fill in the instance name
        await page.fill('input[name="instanceName"]', 'BillingSvc')

        # Select status "Inactive" (assuming a dropdown selector)
        await page.select_option('select[name="status"]', 'Inactive')

        # Submit the creation form
        await page.click('button#save-instance')

        # ------------------------------------------------------------
        # 3. Verify the instance appears with status "Inactive"
        # ------------------------------------------------------------
        # Locate the table row that contains the newly created instance
        row_selector = 'tr:has-text("BillingSvc")'
        await expect(page.locator(row_selector)).to_be_visible()

        # Verify the status cell shows "Inactive"
        status_cell = page.locator(f"{row_selector} >> td.status")
        await expect(status_cell).to_have_text('Inactive')

        # ------------------------------------------------------------
        # 4. Activate the instance
        # ------------------------------------------------------------
        # Click the Activate button/toggle within the same row
        activate_button = page.locator(f"{row_selector} >> button.activate")
        await activate_button.click()

        # ------------------------------------------------------------
        # 5. Verify status changes to "Active" and success message appears
        # ------------------------------------------------------------
        await expect(status_cell).to_have_text('Active')
        await expect(page.locator('text=Instance activated')).to_be_visible()

        # Clean up
        await browser.close()

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(test_activate_service_instance())
