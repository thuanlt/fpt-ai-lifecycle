import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – adjust these values to match your environment
# ---------------------------------------------------------------------------
URL = "https://your-application-domain.com/service-catalog"  # <-- replace with actual URL
SERVICE_CODE_INPUT_SELECTOR = "input[name='serviceCode']"   # <-- replace with actual selector for Service Code field
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"          # <-- replace with actual selector for the Save button
VALIDATION_MESSAGE_SELECTOR = "text=Service Code must be alphanumeric without spaces"  # <-- replace with actual selector or text for validation message

async def test_service_code_format_validation():
    """Verify that entering a Service Code with spaces triggers a validation error
    and prevents the record from being saved.
    """
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Catalog Management page
        await page.goto(URL)

        # Wait for the Service Code input to be visible
        await page.wait_for_selector(SERVICE_CODE_INPUT_SELECTOR)

        # Fill the Service Code with an invalid value containing a space
        await page.fill(SERVICE_CODE_INPUT_SELECTOR, "ABC 123")

        # Click the Save button
        await page.click(SAVE_BUTTON_SELECTOR)

        # Assert that the validation message appears
        validation_message = page.locator(VALIDATION_MESSAGE_SELECTOR)
        await expect(validation_message).to_be_visible(
            timeout=5000,
            message="Expected validation message for invalid Service Code not displayed"
        )

        # Additionally, ensure that the form is not submitted / record is not saved.
        # This can be verified by checking that we remain on the same page or that the
        # Save button is still enabled (i.e., no navigation occurred).
        # Here we simply assert that the URL has not changed.
        await expect(page).to_have_url(URL, timeout=2000)

        # Clean up
        await context.close()
        await browser.close()

# ---------------------------------------------------------------------------
# Entry point for running the test directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(test_service_code_format_validation())
