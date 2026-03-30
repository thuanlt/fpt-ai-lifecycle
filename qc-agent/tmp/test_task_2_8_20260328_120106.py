import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match the actual application under test
BASE_URL = "http://localhost:3000"  # Replace with the real URL of the Service Registry UI
CREATE_INSTANCE_BUTTON_SELECTOR = "text=Create Service Instance"  # Button that opens the create dialog/form
NAME_INPUT_SELECTOR = "input[name='name']"
TYPE_DROPDOWN_SELECTOR = "select[name='type']"
VERSION_INPUT_SELECTOR = "input[name='version']"
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"
SUCCESS_TOAST_SELECTOR = "text=Instance created successfully"
INSTANCE_LIST_ROW_SELECTOR = "tr:has-text('InventorySvc')"

async def create_service_instance(page):
    # Open the create instance form/dialog
    await page.click(CREATE_INSTANCE_BUTTON_SELECTOR)

    # Fill mandatory fields
    await page.fill(NAME_INPUT_SELECTOR, "InventorySvc")
    await page.select_option(TYPE_DROPDOWN_SELECTOR, label="Inventory")
    await page.fill(VERSION_INPUT_SELECTOR, "2.1.0")

    # Submit the form
    await page.click(SAVE_BUTTON_SELECTOR)

    # Verify success toast appears
    await expect(page.locator(SUCCESS_TOAST_SELECTOR)).to_be_visible(timeout=5000)

    # Verify the new instance appears in the instance list with correct details
    row = page.locator(INSTANCE_LIST_ROW_SELECTOR)
    await expect(row).to_be_visible(timeout=5000)
    # Additional detail checks (optional)
    await expect(row.locator("td:nth-child(2)")) .to_have_text("Inventory")
    await expect(row.locator("td:nth-child(3)")) .to_have_text("2.1.0")

async def run_test():
    async with async_playwright() as p:
        # Choose the browser you prefer (chromium, firefox, webkit)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(BASE_URL)

        # Perform the test steps
        await create_service_instance(page)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
