import asyncio
from playwright.async_api import async_playwright, expect

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Registry page (replace with actual URL)
        await page.goto("https://example.com/service-registry")

        async def create_instance(name: str, service_type: str):
            """Helper to fill the Create Service Instance form and submit."""
            # Open the create‑instance dialog/modal
            await page.click('button#create-instance')
            # Fill instance name
            await page.fill('input[name="instanceName"]', name)
            # Select service type from dropdown (using visible label)
            await page.select_option('select[name="serviceType"]', label=service_type)
            # Submit the form
            await page.click('button#save-instance')

        # -----------------------------------------------------------------
        # Step 1: Create a new instance – expect success
        # -----------------------------------------------------------------
        await create_instance("OrderService", "Payment")
        success_toast = page.locator('text=Instance created successfully')
        await expect(success_toast).to_be_visible(timeout=5000)

        # -----------------------------------------------------------------
        # Step 2: Attempt to create a duplicate instance – expect validation error
        # -----------------------------------------------------------------
        await create_instance("OrderService", "Payment")
        error_msg = page.locator('text=Instance name must be unique within the selected service type')
        await expect(error_msg).to_be_visible(timeout=5000)

        await browser.close()

asyncio.run(run_test())
