import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the Service Registry page
        await page.goto("http://localhost:3000/service-registry")
        await page.wait_for_load_state("networkidle")

        # ------------------------------------------------------------
        # Step 1: Select instance "InventorySvc" and click "Delete"
        # ------------------------------------------------------------
        # Locate the row (or element) that contains the instance name
        instance_row = page.locator("text=InventorySvc").first
        await expect(instance_row).to_be_visible()
        # Click the Delete button that belongs to this row
        delete_button = instance_row.locator('button:has-text("Delete")')
        await delete_button.click()

        # ------------------------------------------------------------
        # Step 2: Confirm deletion (handle confirmation dialog)
        # ------------------------------------------------------------
        # Wait for the confirmation dialog to appear
        confirmation_dialog = page.locator("text=Confirmation")
        await expect(confirmation_dialog).to_be_visible()
        # Click the confirm button inside the dialog (adjust selector if needed)
        await page.locator('button:has-text("Confirm")').click()

        # ------------------------------------------------------------
        # Verify success toast appears
        # ------------------------------------------------------------
        success_toast = page.locator('text=Instance deleted successfully')
        await expect(success_toast).to_be_visible()

        # ------------------------------------------------------------
        # Verify the instance no longer appears in the list
        # ------------------------------------------------------------
        await expect(page.locator('text=InventorySvc')).to_have_count(0)

        await browser.close()

asyncio.run(run())