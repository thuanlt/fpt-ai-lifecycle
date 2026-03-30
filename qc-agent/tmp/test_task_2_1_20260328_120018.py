import asyncio
from playwright.async_api import async_playwright, expect

# Adjust this URL to point to the actual Service Registry page in your environment
SERVICE_REGISTRY_URL = "http://localhost:3000/service-registry"

async def test_create_instance_button_visible():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Navigate to the Service Registry page
        await page.goto(SERVICE_REGISTRY_URL)
        # Wait for the main content to load – adjust selector as needed
        await page.wait_for_selector("text=Service Registry", timeout=10000)
        # Expected Result: The page loads displaying a list of existing services
        # (Implicitly verified by the presence of the heading above)

        # Expected Result: The "Create Instance" button is displayed prominently
        create_instance_button = page.locator("button:has-text('Create Instance')")
        await expect(create_instance_button).to_be_visible()

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_create_instance_button_visible())
