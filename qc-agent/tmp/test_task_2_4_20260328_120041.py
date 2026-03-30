import asyncio
from playwright.async_api import async_playwright, expect

async def test_create_instance_validation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to Service Registry page (replace with actual URL)
        await page.goto("http://localhost:8080/service-registry")
        # Click 'Create Instance' button
        await page.click("text=Create Instance")
        # Assume mandatory fields are left empty; directly click Save
        await page.click("text=Save")
        # Verify validation messages for each mandatory field
        # Adjust selectors to match the application's DOM
        validation_selectors = [
            "css=.error-message[for='serviceName']",
            "css=.error-message[for='instanceId']",
            "css=.error-message[for='version']"
        ]
        for selector in validation_selectors:
            await expect(page.locator(selector)).to_be_visible()
        await browser.close()

asyncio.run(test_create_instance_validation())
