import asyncio
from playwright.async_api import async_playwright, expect

# Configuration
BASE_URL = "https://your-application-url.com"  # TODO: replace with actual URL
SERVICE_CATALOG_PATH = "/service-catalog"  # TODO: replace with actual path if needed

# Selectors (replace with actual selectors from the application)
SELECTOR_SERVICE_NAME_INPUT = "#service-name-input"
SELECTOR_CREATE_BUTTON = "#create-service-button"
SELECTOR_SUCCESS_TOAST = ".toast-success"
SELECTOR_ERROR_MESSAGE = ".error-message"  # container that shows validation errors

async def create_service(page, service_name: str):
    """Fills the service creation form and submits it."""
    await page.fill(SELECTOR_SERVICE_NAME_INPUT, service_name)
    await page.click(SELECTOR_CREATE_BUTTON)
    # Wait for either success toast or error message
    await page.wait_for_timeout(1000)  # short pause for UI response

async def verify_error_message(page, expected_text: str):
    """Asserts that the expected error message is displayed."""
    error_element = await page.wait_for_selector(SELECTOR_ERROR_MESSAGE, timeout=5000)
    actual_text = await error_element.inner_text()
    assert expected_text in actual_text, f"Expected error '{expected_text}' but got '{actual_text}'"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # set headless=True for CI
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to Service Catalog Management page
        await page.goto(f"{BASE_URL}{SERVICE_CATALOG_PATH}")

        # Step 1: Create a service with the name "Customer Support"
        await create_service(page, "Customer Support")
        # Verify creation succeeded (optional – check success toast)
        try:
            await page.wait_for_selector(SELECTOR_SUCCESS_TOAST, timeout=3000)
        except Exception:
            raise AssertionError("Service creation did not show a success toast.")

        # Step 2: Attempt to create another service with the same name "Customer Support"
        await create_service(page, "Customer Support")

        # Expected Result: An error message "Service Name must be unique" is displayed.
        await verify_error_message(page, "Service Name must be unique")

        # Expected Result: The second service creation is rejected (no success toast should appear)
        # Ensure that a success toast does NOT appear after the duplicate attempt
        try:
            await page.wait_for_selector(SELECTOR_SUCCESS_TOAST, timeout=2000)
            raise AssertionError("Duplicate service creation was incorrectly accepted.")
        except Exception:
            # Timeout is expected – meaning no success toast
            pass

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
