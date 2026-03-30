import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Navigate to the Service Catalog Management page
        # ------------------------------------------------------------
        await page.goto("https://your-application-url.com/service-catalog")
        await page.wait_for_load_state("networkidle")

        # ------------------------------------------------------------
        # Helper function to create a service with a given code
        # ------------------------------------------------------------
        async def create_service(service_code: str):
            # Click the button/link that opens the "Add Service" form
            await page.click('text="Add Service"')
            await page.wait_for_selector('form#serviceForm')

            # Fill mandatory fields – adjust selectors to match your app
            await page.fill('input[name="serviceCode"]', service_code)
            # Example of another required field (replace with real ones)
            await page.fill('input[name="serviceName"]', "Test Service")

            # Submit the form
            await page.click('button:has-text("Save")')

        # ------------------------------------------------------------
        # Step 1: Save a service with code "SRV001"
        # ------------------------------------------------------------
        await create_service("SRV001")
        # Wait for a success toast/notification (adjust selector as needed)
        await page.wait_for_selector('text="Service saved successfully"', timeout=5000)

        # ------------------------------------------------------------
        # Step 2: Attempt to save another service with the same code
        # ------------------------------------------------------------
        await create_service("SRV001")

        # ------------------------------------------------------------
        # Verification: Expect duplicate‑code error message
        # ------------------------------------------------------------
        error_locator = await page.wait_for_selector(
            'text="Service Code must be unique"', timeout=5000
        )
        assert error_locator is not None, "Error message for duplicate Service Code was not displayed"

        # Optional: ensure the second save did not succeed (still on the form)
        # await page.wait_for_selector('form#serviceForm')

        await browser.close()

asyncio.run(run())
