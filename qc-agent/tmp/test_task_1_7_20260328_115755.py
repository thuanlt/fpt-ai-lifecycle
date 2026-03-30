import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "https://your-application-url.com"  # TODO: replace with actual base URL
SERVICE_ID = "12345"  # TODO: replace with the ID of the service to be edited
NEW_DESCRIPTION = "Updated service description via automated test"

# ---------------------------------------------------------------------------
# Selectors (replace with actual selectors from the application)
# ---------------------------------------------------------------------------
SELECTORS = {
    "service_detail_view": f"a[href='/services/{SERVICE_ID}']",
    "edit_button": "button[data-test-id='edit-service']",
    "description_textarea": "textarea[name='description']",
    "save_button": "button[data-test-id='save-service']",
    "detail_description": "div[data-test-id='service-description']",
    "list_row_description": f"tr[data-service-id='{SERVICE_ID}'] td[data-test-id='description']",
    "updated_timestamp": "span[data-test-id='service-updated-timestamp']",
}

async def update_service_description(page):
    """Performs the steps to update a service description and validates the outcome."""
    # 1. Navigate to the service detail view
    await page.goto(f"{BASE_URL}/services/{SERVICE_ID}")
    await expect(page.locator(SELECTORS["service_detail_view"]))

    # 2. Click the Edit button
    await page.click(SELECTORS["edit_button"])

    # 3. Modify the Description field
    description_field = page.locator(SELECTORS["description_textarea"])
    await description_field.fill(NEW_DESCRIPTION)

    # 4. Click Save
    await page.click(SELECTORS["save_button"])

    # -----------------------------------------------------------------------
    # Expected Results
    # -----------------------------------------------------------------------
    # - => Service information is updated successfully
    # Verify a success toast/notification appears (placeholder selector)
    success_toast = page.locator("div[data-test-id='toast-success']")
    await expect(success_toast).to_be_visible(timeout=5000)

    # - => Updated Description is reflected in the detail view and list
    detail_desc = page.locator(SELECTORS["detail_description"])
    await expect(detail_desc).to_have_text(NEW_DESCRIPTION)

    list_desc = page.locator(SELECTORS["list_row_description"])
    await expect(list_desc).to_have_text(NEW_DESCRIPTION)

    # - => Updated timestamp is shown
    timestamp = page.locator(SELECTORS["updated_timestamp"])
    await expect(timestamp).to_be_visible()
    # Optionally, you could verify that the timestamp is recent.

async def run_test():
    async with async_playwright() as p:
        # Choose the browser you prefer (chromium, firefox, webkit)
        browser = await p.chromium.launch(headless=False)  # Set headless=True for CI
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await update_service_description(page)
            print("✅ Test passed: Service description updated and verified.")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
