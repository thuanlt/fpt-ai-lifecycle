import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match the actual application under test
BASE_URL = "https://your-app-domain.com"  # Base URL of the application
SERVICE_REGISTRY_PATH = "/service-registry"  # Path to the Service Registry page
CREATE_INSTANCE_BUTTON_SELECTOR = "text=Create Instance"  # Selector for the button that opens the Create Instance dialog
CANCEL_BUTTON_SELECTOR = "button:has-text(\"Cancel\")"  # Selector for the Cancel button inside the dialog
INSTANCE_DIALOG_SELECTOR = "#create-instance-dialog"  # Root selector for the Create Instance dialog
INSTANCE_LIST_ROWS_SELECTOR = "#instance-list tbody tr"  # Selector for rows in the instance list table

async def verify_cancel_closes_dialog_without_persisting(page):
    # Navigate to the Service Registry page
    await page.goto(f"{BASE_URL}{SERVICE_REGISTRY_PATH}")

    # Capture the current number of instances displayed in the list
    initial_rows = await page.locator(INSTANCE_LIST_ROWS_SELECTOR).count()

    # Open the Create Instance dialog
    await page.click(CREATE_INSTANCE_BUTTON_SELECTOR)
    # Ensure the dialog is visible
    await expect(page.locator(INSTANCE_DIALOG_SELECTOR)).to_be_visible()

    # Click the Cancel button
    await page.click(CANCEL_BUTTON_SELECTOR)

    # Verify the dialog is closed
    await expect(page.locator(INSTANCE_DIALOG_SELECTOR)).to_be_hidden()

    # Verify the user is back on the Service Registry list (URL may stay the same, so we just check the list visibility)
    await expect(page.locator(INSTANCE_LIST_ROWS_SELECTOR).first).to_be_visible()

    # Verify that no new instance has been added to the list
    final_rows = await page.locator(INSTANCE_LIST_ROWS_SELECTOR).count()
    assert final_rows == initial_rows, f"Instance count changed after cancel: {initial_rows} -> {final_rows}"

async def main():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await verify_cancel_closes_dialog_without_persisting(page)
            print("✅ Test passed: Cancel button closes dialog without persisting data.")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
