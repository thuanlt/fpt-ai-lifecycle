import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Test Case: Invalid Transition - Retired → Active
# Steps:
#   1. Navigate to the Service Management page.
#   2. Locate a service whose current status is "Retired".
#   3. Attempt to change its status to "Active".
#   4. Verify that the system displays the error message
#      "Invalid status transition".
#   5. Verify that the service status remains "Retired".
# ---------------------------------------------------------------------------

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # 1. Navigate to the Service Management page
        # ---------------------------------------------------------------
        # TODO: Replace with the actual URL of the Service Management UI
        await page.goto("https://your-application-domain.com/service-management")
        await page.wait_for_load_state("networkidle")

        # ---------------------------------------------------------------
        # 2. Locate a service with status "Retired"
        # ---------------------------------------------------------------
        # Assuming each service is listed in a table row (<tr>) and the status
        # is displayed in a cell with a data-test-id attribute.
        # Adjust the selector according to the real DOM structure.
        retired_service_row = page.locator("tr:has(td[data-test-id='service-status'] >> text=Retired')").first
        await expect(retired_service_row).to_be_visible(timeout=5000)

        # Store a unique identifier for later verification (e.g., service name or ID)
        service_name = await retired_service_row.locator("td[data-test-id='service-name']").inner_text()

        # ---------------------------------------------------------------
        # 3. Attempt to change its status to "Active"
        # ---------------------------------------------------------------
        # Click the "Edit" button for the selected service
        edit_button = retired_service_row.locator("button[data-test-id='edit-service']")
        await edit_button.click()

        # Wait for the edit modal/dialog to appear
        edit_modal = page.locator("div[data-test-id='service-edit-modal']")
        await expect(edit_modal).to_be_visible()

        # Change the status via a dropdown/select element
        status_dropdown = edit_modal.locator("select[data-test-id='service-status-select']")
        await status_dropdown.select_option(label="Active")

        # Submit the change
        save_button = edit_modal.locator("button[data-test-id='save-service']")
        await save_button.click()

        # ---------------------------------------------------------------
        # 4. Verify error message "Invalid status transition"
        # ---------------------------------------------------------------
        # Assuming the application shows a toast/alert with a specific test id
        error_toast = page.locator("div[data-test-id='toast-error'] >> text=Invalid status transition")
        await expect(error_toast).to_be_visible(timeout=5000)

        # ---------------------------------------------------------------
        # 5. Verify that the service status is still "Retired"
        # ---------------------------------------------------------------
        # Refresh the row (or re-fetch) to ensure UI reflects latest state
        await page.reload()
        await page.wait_for_load_state("networkidle")
        refreshed_row = page.locator(f"tr:has(td[data-test-id='service-name'] >> text={service_name})")
        await expect(refreshed_row).to_be_visible()
        status_cell = refreshed_row.locator("td[data-test-id='service-status']")
        await expect(status_cell).to_have_text("Retired")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
