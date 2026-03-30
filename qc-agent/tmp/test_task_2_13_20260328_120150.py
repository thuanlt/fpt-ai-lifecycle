import asyncio
from playwright.async_api import async_playwright, expect

# Constants – adjust these values to match the actual environment
BASE_URL = "https://your-app-domain.com/service-registry"  # TODO: replace with real URL
INSTANCE_NAME = "BillingSvc"
SUCCESS_MESSAGE = "Instance deactivated"

async def deactivate_instance(page):
    """Locate the instance row, verify it is Active, deactivate it and verify the outcome."""
    # Wait for the table that lists service instances to be visible
    await page.wait_for_selector("table")

    # Locate the row that contains the instance name
    row_locator = page.locator(f"tr:has-text('{INSTANCE_NAME}')")
    await expect(row_locator).to_be_visible(timeout=5000)

    # Verify the current status is "Active"
    status_cell = row_locator.locator("td.status")  # assumes a CSS class 'status' on the status column
    await expect(status_cell).to_have_text("Active", timeout=3000)
    print(f"[INFO] Instance '{INSTANCE_NAME}' is initially Active.")

    # Click the Deactivate button/toggle within the same row
    deactivate_button = row_locator.locator("button:has-text('Deactivate'), input[type='checkbox'][aria-label='Deactivate']")
    await expect(deactivate_button).to_be_enabled()
    await deactivate_button.click()
    print("[ACTION] Clicked Deactivate button.")

    # Verify the status column now shows "Inactive"
    await expect(status_cell).to_have_text("Inactive", timeout=5000)
    print(f"[VERIFY] Status changed to Inactive for instance '{INSTANCE_NAME}'.")

    # Verify the success toast/message appears
    toast_locator = page.locator(f"text={SUCCESS_MESSAGE}")
    await expect(toast_locator).to_be_visible(timeout=5000)
    print(f"[VERIFY] Success message '{SUCCESS_MESSAGE}' displayed.")

async def run_test():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Registry page
        await page.goto(BASE_URL)
        print(f"[NAVIGATE] Opened {BASE_URL}")

        # Perform the deactivate‑instance scenario
        await deactivate_instance(page)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
