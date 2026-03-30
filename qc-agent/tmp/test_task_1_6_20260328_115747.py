import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – replace these values with the real environment URLs/selectors
# ---------------------------------------------------------------------------
SERVICE_LIST_URL = "https://example.com/services"  # URL of the service list page

# Selectors (CSS or text) – adjust according to the actual application UI
SERVICE_NAME_LINK_SELECTOR = "css=table >> tbody >> tr >> td >> a.service-name"  # link to a service name in the list
SERVICE_DETAIL_CONTAINER = "css=div.service-detail"                     # container that appears on the detail view
STATUS_SPAN_SELECTOR = "span.status"                                   # element that displays the service status
EDIT_BUTTON_SELECTOR = "button#edit-service"                           # Edit button on the detail page

# Expected field labels that must be visible on the detail page
EXPECTED_FIELD_LABELS = [
    "Service Name",
    "Description",
    "Version",
    "Status",
    "Owner",
]

async def test_read_service_details():
    """Automates the 'Read Service Details' scenario.

    Steps:
    1. Navigate to the service list page.
    2. Click on a service name to open its detail view.
    3. Verify that the detail page loads and all required fields are visible.
    4. Verify that the Edit button is present.
    5. If the service status is "Retired", assert that the Edit button is disabled.
    """
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # 1. Open the service list page
        # ---------------------------------------------------------------
        await page.goto(SERVICE_LIST_URL)

        # ---------------------------------------------------------------
        # 2. Click on the first service name in the list
        # ---------------------------------------------------------------
        service_link = page.locator(SERVICE_NAME_LINK_SELECTOR).first
        await service_link.click()

        # ---------------------------------------------------------------
        # 3. Wait for the detail view to appear and validate fields
        # ---------------------------------------------------------------
        await page.wait_for_selector(SERVICE_DETAIL_CONTAINER)
        for label in EXPECTED_FIELD_LABELS:
            field_locator = page.locator(f"text={label}")
            await expect(field_locator).to_be_visible()

        # ---------------------------------------------------------------
        # 4. Verify Edit button presence
        # ---------------------------------------------------------------
        edit_button = page.locator(EDIT_BUTTON_SELECTOR)
        await expect(edit_button).to_be_visible()

        # ---------------------------------------------------------------
        # 5. Validate Edit button state based on service status
        # ---------------------------------------------------------------
        status_element = page.locator(STATUS_SPAN_SELECTOR)
        status_text = (await status_element.inner_text()).strip().lower()
        if status_text == "retired":
            await expect(edit_button).to_be_disabled()
        else:
            await expect(edit_button).to_be_enabled()

        # Clean up
        await context.close()
        await browser.close()

# Entry point for direct execution
if __name__ == "__main__":
    asyncio.run(test_read_service_details())
