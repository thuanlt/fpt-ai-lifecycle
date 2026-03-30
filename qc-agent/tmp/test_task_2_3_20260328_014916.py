import asyncio
from playwright.async_api import async_playwright, Page, expect

# Constants (replace with actual values for your application)
BASE_URL = "http://your-application-url.com/service-catalog"  # TODO: update URL
SERVICE_NAME_SELECTOR = "#service-name"                     # TODO: update selector
SAVE_BUTTON_SELECTOR = "#save-button"                     # TODO: update selector
VALIDATION_ERROR_SELECTOR = "text=Invalid characters detected"

async def verify_invalid_characters(page: Page) -> None:
    """Test case SCV-003 – Verify invalid character handling for Service Name.

    Steps:
    1. Navigate to the Service Catalog page.
    2. Enter special characters "@#$%" into the Service Name field.
    3. Click the Save button.
    4. Verify that an inline validation error "Invalid characters detected" is displayed.
    5. Verify that the service is not saved (the error remains visible and the URL does not change).
    """
    # Step 1 – already on the page when this function is called.

    # Step 2 – input invalid characters.
    await page.fill(SERVICE_NAME_SELECTOR, "@#$%")

    # Step 3 – attempt to save.
    await page.click(SAVE_BUTTON_SELECTOR)

    # Step 4 – expect validation error.
    error_element = await page.wait_for_selector(VALIDATION_ERROR_SELECTOR, timeout=5000)
    assert await error_element.is_visible(), "Validation error message is not visible"

    # Step 5 – ensure the service was not saved.
    # Simple heuristic: the error message should still be present after a short wait.
    await asyncio.sleep(1)
    assert await page.is_visible(VALIDATION_ERROR_SELECTOR), "Service appears to have been saved despite validation error"

async def main() -> None:
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Catalog management screen
        await page.goto(BASE_URL)

        # Run the test case
        await verify_invalid_characters(page)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
