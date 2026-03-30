import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – adjust these values to match your environment
# ---------------------------------------------------------------------------
BASE_URL = "https://your-application-domain.com"  # TODO: replace with actual base URL
SERVICE_CATALOG_PATH = "/service-catalog"       # TODO: replace with actual path to the Service Catalog Management page

# Selectors – update these to match the actual DOM structure of your app
SLA_INPUT_SELECTOR = "input[name='sla']"          # Selector for the SLA input field
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"  # Selector for the Save button
VALIDATION_ERROR_SELECTOR = "text=SLA must be in HH:MM:SS format"  # Exact error message selector
SUCCESS_TOAST_SELECTOR = "text=Service saved successfully"   # Selector for success confirmation (toast/message)

async def test_sla_field_validation():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # -------------------------------------------------------------------
        # Step 1: Navigate to the Service Catalog Management page
        # -------------------------------------------------------------------
        await page.goto(f"{BASE_URL}{SERVICE_CATALOG_PATH}")
        await page.wait_for_load_state("networkidle")

        # -------------------------------------------------------------------
        # Step 2: Enter an invalid SLA value and attempt to save
        # -------------------------------------------------------------------
        await page.fill(SLA_INPUT_SELECTOR, "25:61:00")
        await page.click(SAVE_BUTTON_SELECTOR)

        # Verify that the validation error is displayed
        error_element = page.locator(VALIDATION_ERROR_SELECTOR)
        await expect(error_element).to_be_visible()
        # Ensure that the save operation was blocked (still on the same page)
        await expect(page).to_have_url(f"{BASE_URL}{SERVICE_CATALOG_PATH}")

        # -------------------------------------------------------------------
        # Step 3: Clear the SLA field (leave it blank) and save again
        # -------------------------------------------------------------------
        await page.fill(SLA_INPUT_SELECTOR, "")
        await page.click(SAVE_BUTTON_SELECTOR)

        # Verify that the service is saved successfully (optional toast/message)
        success_toast = page.locator(SUCCESS_TOAST_SELECTOR)
        await expect(success_toast).to_be_visible()

        # Clean up
        await context.close()
        await browser.close()

# ---------------------------------------------------------------------------
# Entry point for running the test directly via ``python script_name.py``
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(test_sla_field_validation())
