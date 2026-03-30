import asyncio
from playwright.async_api import async_playwright

async def test_status_transition():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the Service Management page (replace with actual URL)
        await page.goto("https://example.com/service-management")
        # Assume we are already on a service in Draft status; locate the service row
        # Click on the service to open edit dialog
        await page.click('text=Draft')  # placeholder selector for the Draft service
        # Open status dropdown
        await page.click('#service-status-dropdown')
        # Select "Active" option
        await page.click('text=Active')
        # Click Save
        await page.click('#save-button')
        # Wait for success toast/message
        await page.wait_for_selector('text=Status changes successfully', timeout=5000)
        # Verify the service now appears with status "Active" in the list
        await page.wait_for_selector('.service-row >> text=Active', timeout=5000)
        print("Test passed: Service status transitioned to Active.")
        await context.close()
        await browser.close()

asyncio.run(test_status_transition())