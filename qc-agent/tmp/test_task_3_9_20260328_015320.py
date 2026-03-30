import asyncio
from playwright.async_api import async_playwright, Page, Route, Request

# Adjust these constants to match the actual application under test
APP_URL = "http://localhost:3000"  # Base URL of the Service Catalog application
CREATE_SERVICE_BUTTON_SELECTOR = "text=Create New Service"  # Button to open the create form
SERVICE_NAME_INPUT_SELECTOR = "#service-name"  # Input for service name
SERVICE_DESC_INPUT_SELECTOR = "#service-description"  # Input for service description
SAVE_BUTTON_SELECTOR = "text=Save"  # Save button inside the form
ERROR_DIALOG_SELECTOR = ".error-dialog, text=Unable to save service"  # Selector or text for the error message
# The API endpoint that handles service creation – adjust the path as needed
SERVICE_CREATION_API_PATTERN = "**/api/services"  # Wildcard pattern for request interception

async def mock_service_creation_error(route: Route, request: Request):
    """Intercept the service‑creation POST request and force a 500 response."""
    if request.method.upper() == "POST":
        await route.fulfill(
            status=500,
            body="{\"error\": \"Internal Server Error\"}",
            headers={"Content-Type": "application/json"},
        )
    else:
        # Allow other requests to pass through unchanged
        await route.continue_()

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page: Page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Set up request mocking for the service‑creation endpoint
        # ------------------------------------------------------------
        await context.route(SERVICE_CREATION_API_PATTERN, mock_service_creation_error)

        # ------------------------------------------------------------
        # 2. Navigate to the application and open the "Create New Service" form
        # ------------------------------------------------------------
        await page.goto(APP_URL)
        await page.click(CREATE_SERVICE_BUTTON_SELECTOR)

        # ------------------------------------------------------------
        # 3. Fill the form with valid data
        # ------------------------------------------------------------
        await page.fill(SERVICE_NAME_INPUT_SELECTOR, "Test Service")
        await page.fill(SERVICE_DESC_INPUT_SELECTOR, "A description for the test service.")

        # ------------------------------------------------------------
        # 4. Submit the form – the mocked 500 response will be triggered
        # ------------------------------------------------------------
        await page.click(SAVE_BUTTON_SELECTOR)

        # ------------------------------------------------------------
        # 5. Verify that the error dialog/message is displayed
        # ------------------------------------------------------------
        # Wait for either the dialog element or the exact error text to appear
        try:
            await page.wait_for_selector(ERROR_DIALOG_SELECTOR, timeout=5000)
            print("✅ Error dialog/message displayed as expected.")
        except Exception as e:
            print("❌ Expected error dialog/message was NOT displayed.")
            raise e

        # ------------------------------------------------------------
        # 6. Verify that the form remains open (i.e., the name input is still visible)
        # ------------------------------------------------------------
        is_form_still_visible = await page.is_visible(SERVICE_NAME_INPUT_SELECTOR)
        if is_form_still_visible:
            print("✅ Form remains open for user correction/retry.")
        else:
            print("❌ Form is not visible; it may have been closed unexpectedly.")
            raise AssertionError("Form closed after error response.")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
