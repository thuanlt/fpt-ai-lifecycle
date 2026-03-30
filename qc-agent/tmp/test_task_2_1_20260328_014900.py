import asyncio
from playwright.async_api import async_playwright, expect

# -----------------------------------------------------------------------------
# Test Case: SCV-001 Verify that Service Name cannot be left empty
# Steps:
# 1. Navigate to the Service Catalog creation page.
# 2. Fill all mandatory fields except "Service Name" (leave it blank).
# 3. Attempt to click the Save button.
# 4. Verify that an inline validation error is shown and the save action is blocked.
# -----------------------------------------------------------------------------

# NOTE: Replace the URL and selector values with the actual ones from the application.
SERVICE_CATALOG_URL = "https://your-application-domain.com/service-catalog/create"
SERVICE_NAME_INPUT_SELECTOR = "input[name='serviceName']"  # Adjust as needed
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"          # Adjust as needed
ERROR_MESSAGE_SELECTOR = "text=Service Name is required"  # Adjust as needed

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Navigate to the Service Catalog creation page
        await page.goto(SERVICE_CATALOG_URL)

        # OPTIONAL: Wait for the form to be visible (adjust selector if needed)
        await page.wait_for_selector(SAVE_BUTTON_SELECTOR)

        # Step 2: Fill all mandatory fields except Service Name
        # Example of filling other mandatory fields – replace selectors accordingly
        # await page.fill("input[name='serviceDescription']", "Test description")
        # await page.fill("input[name='serviceOwner']", "owner@example.com")
        # Add additional field fills here as required by the application

        # Intentionally leave Service Name blank – ensure the field is cleared
        await page.fill(SERVICE_NAME_INPUT_SELECTOR, "")

        # Step 3: Attempt to click the Save button
        # The button might be disabled; we attempt a click and catch any errors
        try:
            await page.click(SAVE_BUTTON_SELECTOR, timeout=2000)
        except Exception:
            # If the button is disabled, Playwright will raise a timeout/error.
            # This is acceptable as part of the validation.
            pass

        # Step 4: Verify validation error message is displayed
        # Using Playwright's expect API for a robust assertion
        error_element = page.locator(ERROR_MESSAGE_SELECTOR)
        await expect(error_element).to_be_visible(timeout=5000)
        # Additionally, ensure the Save operation did not succeed (still on the same page)
        await expect(page).to_have_url(SERVICE_CATALOG_URL)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
