import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these selectors according to the actual application under test
SERVICE_NAME_INPUT_SELECTOR = "#service-name-input"   # Input field for Service Name
SAVE_BUTTON_SELECTOR = "#save-service-button"       # Button to submit/create service
ERROR_MESSAGE_SELECTOR = "//div[contains(@class, 'error') and contains(text(), 'Service Name is required')]"
MODAL_SELECTOR = "#service-creation-modal"          # Modal container selector

async def test_service_name_required_validation():
    async with async_playwright() as p:
        # Launch browser (Chromium) – you can change to firefox or webkit if needed
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # -----------------------------------------------------------------
        # STEP 1: Navigate to the Service Management page where the creation UI is available
        # -----------------------------------------------------------------
        await page.goto("https://your-application-url.com/service-management")
        # Wait for the creation modal to be visible (or trigger it if needed)
        await page.wait_for_selector(MODAL_SELECTOR, state="visible")

        # -----------------------------------------------------------------
        # STEP 2: Ensure the Service Name field is empty
        # -----------------------------------------------------------------
        # Clear any pre‑filled value just in case
        await page.fill(SERVICE_NAME_INPUT_SELECTOR, "")

        # -----------------------------------------------------------------
        # STEP 3: Click the Save/Create button
        # -----------------------------------------------------------------
        await page.click(SAVE_BUTTON_SELECTOR)

        # -----------------------------------------------------------------
        # EXPECTED RESULT 1: Validation error message is displayed
        # -----------------------------------------------------------------
        error_message_element = await page.wait_for_selector(ERROR_MESSAGE_SELECTOR, timeout=5000)
        # Verify the exact text (optional but recommended)
        await expect(error_message_element).to_have_text("Service Name is required")

        # -----------------------------------------------------------------
        # EXPECTED RESULT 2: Service is not created and modal remains open
        # -----------------------------------------------------------------
        # The modal should still be visible
        await expect(page.locator(MODAL_SELECTOR)).to_be_visible()
        # Optionally, verify that no new service row appears in the service list.
        # This part depends on the DOM structure of the service list; placeholder example:
        # await expect(page.locator("text=YourNewServiceName")).to_have_count(0)

        # Clean up
        await context.close()
        await browser.close()

# ---------------------------------------------------------------------
# Entry point for running the script directly
# ---------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(test_service_name_required_validation())
