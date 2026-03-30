import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Test Case: SCV-018 Verify that **Status** dropdown only allows predefined values
# (Active, Inactive, Deprecated)
# ---------------------------------------------------------------------------

# Adjust these constants to match the actual application under test
APP_URL = "https://your-application-url.com/service-catalog"  # <-- replace with real URL
STATUS_DROPDOWN_SELECTOR = "#status"                     # <-- replace with real selector
SAVE_BUTTON_SELECTOR = "#saveBtn"                       # <-- replace with real selector
ERROR_MESSAGE_SELECTOR = ".error-message"               # <-- replace with real selector
EXPECTED_ERROR_TEXT = "Invalid status selected"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # Step 1: Navigate to the Service Catalog Management page
        # ---------------------------------------------------------------
        await page.goto(APP_URL)
        await page.wait_for_load_state("networkidle")

        # ---------------------------------------------------------------
        # Step 2: Attempt to inject an invalid value into the Status dropdown
        # ---------------------------------------------------------------
        # We use JavaScript to set a value that is not part of the predefined list.
        invalid_value = "InvalidStatus"
        await page.evaluate(
            f"""
            const dropdown = document.querySelector('{STATUS_DROPDOWN_SELECTOR}');
            if (dropdown) {{
                dropdown.value = '{invalid_value}';
                // Trigger change event so the UI reacts as if a user selected it
                const event = new Event('change', {{ bubbles: true }});
                dropdown.dispatchEvent(event);
            }}
            """
        )

        # ---------------------------------------------------------------
        # Step 3: Click the Save button
        # ---------------------------------------------------------------
        await page.click(SAVE_BUTTON_SELECTOR)

        # ---------------------------------------------------------------
        # Step 4: Verify that the system rejects the value and shows the error
        # ---------------------------------------------------------------
        # Wait for the error message to appear and validate its text.
        error_element = page.locator(ERROR_MESSAGE_SELECTOR)
        await expect(error_element).to_be_visible(timeout=5000)
        await expect(error_element).to_have_text(EXPECTED_ERROR_TEXT)

        # ---------------------------------------------------------------
        # Step 5: Ensure that the Save operation is blocked (i.e., no navigation)
        # ---------------------------------------------------------------
        # One simple way is to assert that we are still on the same URL.
        await expect(page).to_have_url(APP_URL)

        print("✅ SCV-018 passed: Invalid status value was correctly rejected.")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
