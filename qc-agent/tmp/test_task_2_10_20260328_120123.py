import asyncio
from playwright.async_api import async_playwright

async def test_update_service_instance():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Registry page (replace with actual URL)
        await page.goto("https://example.com/service-registry")

        # Locate the row that contains the instance "InventorySvc" and click its Edit button
        row = page.locator("tr", has_text="InventorySvc")
        await row.locator("button:has-text('Edit')").click()

        # Wait for the edit form to appear
        await page.wait_for_selector("form#edit-instance-form")

        # (Optional) Verify that the form is pre‑populated with current data
        # await expect(page.locator("input[name='serviceName']")).to_have_value("InventorySvc")

        # Change the Version field to "2.2.0"
        await page.fill("input[name='version']", "2.2.0")

        # Click the Update button
        await page.click("button:has-text('Update')")

        # Verify success toast appears
        await page.wait_for_selector("text=Instance updated successfully")

        # Verify the instance list now shows the updated version
        await page.wait_for_selector("tr:has-text('InventorySvc') >> td:has-text('2.2.0')")

        await browser.close()

asyncio.run(test_update_service_instance())