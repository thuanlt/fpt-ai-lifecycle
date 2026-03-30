import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – replace these values with the actual URLs and selectors for
# your application under test.
# ---------------------------------------------------------------------------
BASE_URL = "https://your-app.example.com"  # <-- Update to the Service Catalog URL

# Selectors (use data-testids, aria-labels, or other stable attributes)
SELECTORS = {
    "catalog_list": "css=ul.service-catalog-list",                     # Container for service items
    "service_item": "text=Standard Support",                         # Text selector for the specific service
    "create_button": "text=Create New Service",                     # Button to open the creation form
    "name_input": "[data-test-id='service-name']",                  # Input for service name
    "category_dropdown": "[data-test-id='service-category']",      # Category dropdown
    "category_option": "text=Support",                               # Example category option
    "description_input": "[data-test-id='service-description']",   # Description textarea
    "save_button": "text=Save",                                     # Save button in the form
    "error_message": "css=.error-message",                         # Container for validation errors
}

async def ensure_service_exists(page):
    """Make sure a service named 'Standard Support' is present.
    If it does not exist, create it using the same UI flow.
    """
    await page.goto(f"{BASE_URL}/service-catalog")
    # Wait for the catalog list to load
    await page.wait_for_selector(SELECTORS["catalog_list"])
    # Check if the service already appears
    service_elements = await page.query_selector_all(SELECTORS["service_item"])
    if not service_elements:
        # Service not found – create it
        await page.click(SELECTORS["create_button"])
        await page.fill(SELECTORS["name_input"], "Standard Support")
        await page.click(SELECTORS["category_dropdown"])
        await page.click(SELECTORS["category_option"])
        await page.fill(SELECTORS["description_input"], "Standard support service description")
        await page.click(SELECTORS["save_button"])
        # Verify creation succeeded
        await page.wait_for_selector(SELECTORS["service_item"])
        print("Created prerequisite service 'Standard Support'.")
    else:
        print("Prerequisite service 'Standard Support' already exists.")

async def test_duplicate_service_name(page):
    # Step 1: Ensure the prerequisite service exists (already handled before calling)
    # Step 2: Open the Create New Service form
    await page.click(SELECTORS["create_button"])
    # Fill the form with a duplicate name
    await page.fill(SELECTORS["name_input"], "Standard Support")
    await page.click(SELECTORS["category_dropdown"])
    await page.click(SELECTORS["category_option"])
    await page.fill(SELECTORS["description_input"], "Attempting duplicate entry")
    # Step 3: Click Save
    await page.click(SELECTORS["save_button"])
    # Verify validation error is shown
    error_locator = page.locator(SELECTORS["error_message"])
    await expect(error_locator).to_be_visible()
    await expect(error_locator).to_have_text("A service with this name already exists")
    # Verify that no new duplicate entry appears in the list
    await page.goto(f"{BASE_URL}/service-catalog")
    await page.wait_for_selector(SELECTORS["catalog_list"])
    # Count occurrences of the service name
    items = await page.query_selector_all(SELECTORS["service_item"])
    assert len(items) == 1, "Duplicate service was incorrectly created"
    print("Duplicate service name validation passed.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for CI
        context = await browser.new_context()
        page = await context.new_page()
        # Ensure the prerequisite service exists
        await ensure_service_exists(page)
        # Execute the duplicate name test case
        await test_duplicate_service_name(page)
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
