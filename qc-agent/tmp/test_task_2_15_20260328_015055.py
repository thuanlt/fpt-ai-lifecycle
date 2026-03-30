import asyncio
from playwright.async_api import async_playwright, expect

# Constants – adjust selectors according to the actual application
DESCRIPTION_INPUT_SELECTOR = "#description"          # CSS selector for the Description textarea/input
SAVE_BUTTON_SELECTOR = "#saveButton"               # CSS selector for the Save button
ERROR_MESSAGE_SELECTOR = "#descriptionError"       # CSS selector for the error message element related to Description
EXPECTED_ERROR_TEXT = "Description cannot exceed 500 characters"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless by default). Change to "chromium", "firefox", or "webkit" as needed.
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------------
        # STEP 1: Navigate to the Service Catalog Management page where the form lives.
        # ---------------------------------------------------------------------
        await page.goto("https://your-application-url.com/service-catalog")
        # Wait for the description field to be visible to ensure the page has loaded.
        await page.wait_for_selector(DESCRIPTION_INPUT_SELECTOR)

        # ---------------------------------------------------------------------
        # STEP 2: Input a description that exceeds the maximum allowed length (501 chars).
        # ---------------------------------------------------------------------
        long_description = "A" * 501  # Generate a string of 501 characters.
        await page.fill(DESCRIPTION_INPUT_SELECTOR, long_description)

        # ---------------------------------------------------------------------
        # STEP 3: Attempt to save the form.
        # ---------------------------------------------------------------------
        await page.click(SAVE_BUTTON_SELECTOR)

        # ---------------------------------------------------------------------
        # STEP 4: Verify that the appropriate validation error is displayed and that the save action is blocked.
        # ---------------------------------------------------------------------
        # Wait for the error message to appear.
        error_element = await page.wait_for_selector(ERROR_MESSAGE_SELECTOR, timeout=5000)
        # Assert the error text matches the expected message.
        actual_error_text = await error_element.text_content()
        assert actual_error_text.strip() == EXPECTED_ERROR_TEXT, (
            f"Expected error message '{EXPECTED_ERROR_TEXT}', but got '{actual_error_text}'."
        )
        # Additionally, ensure that we are still on the same page (i.e., navigation did not occur).
        # This can be done by checking that the description field is still present and enabled.
        assert await page.is_visible(DESCRIPTION_INPUT_SELECTOR), "Description field is no longer visible – possible navigation occurred."
        # Optionally, verify that the Save button remains enabled/disabled according to UI rules.
        # Here we just confirm that the form was not submitted successfully.

        print("✅ Test passed: Description field correctly validates maximum length.")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
