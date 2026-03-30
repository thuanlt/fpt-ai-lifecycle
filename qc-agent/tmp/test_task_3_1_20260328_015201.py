import asyncio
from playwright.async_api import async_playwright, expect

# Adjust this URL to point to the actual Service Catalog page in your environment
SERVICE_CATALOG_URL = "http://localhost:3000/service-catalog"

async def test_create_service_button_visible():
    async with async_playwright() as p:
        # Launch a headless Chromium browser; set headless=False for debugging
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Navigate to the Service Catalog main page
        await page.goto(SERVICE_CATALOG_URL)
        # Wait for the main content to load – assuming a table or list with a known selector
        await page.wait_for_selector("#service-list, .service-list, table")
        # Expected Result: The page loads displaying a list of existing services
        # (Implicitly verified by the wait above – if it times out, the test will fail)

        # Expected Result: The "Create Service" button is displayed prominently at the top right corner
        create_button = page.locator("button:has-text('Create Service'), text='Create Service'")
        await expect(create_button).to_be_visible()

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_create_service_button_visible())
