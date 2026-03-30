import asyncio
from playwright.async_api import async_playwright, expect

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Replace this with the actual URL of the Service Catalog page under test.
SERVICE_CATALOG_URL = "https://your-application-domain.com/service-catalog"
# If the form has a specific identifier, adjust the selector below.
FORM_SELECTOR = "form#service-catalog"  # e.g., <form id="service-catalog">...</form>

async def verify_field_default_state(page, field_locator):
    """Verify default value, enabled state, and placeholder for a single field.

    Args:
        page: Playwright page instance.
        field_locator: Locator pointing to the input/textarea/select element.
    """
    # 1. Ensure the field is enabled (editable).
    await expect(field_locator).to_be_enabled()

    # 2. Verify the field's value is empty (or has a default defined in SRS).
    #    For generic purposes we assert empty string; adapt if defaults exist.
    value = await field_locator.input_value()
    assert value == "", f"Expected field to be empty by default, but found '{value}'."

    # 3. Verify placeholder text exists and matches design documentation.
    #    Here we simply assert that a placeholder attribute is present and non‑empty.
    placeholder = await field_locator.get_attribute("placeholder")
    assert placeholder is not None and placeholder.strip() != "", (
        "Placeholder text is missing or empty for the field."
    )

async def main():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless by default).
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Catalog page.
        await page.goto(SERVICE_CATALOG_URL)

        # Wait for the form to be visible.
        form = page.locator(FORM_SELECTOR)
        await expect(form).to_be_visible()

        # Gather all interactive form fields: input, textarea, and select.
        field_locators = form.locator("input, textarea, select")
        count = await field_locators.count()
        assert count > 0, "No input fields were found inside the Service Catalog form."

        # Iterate over each field and perform the default‑state verification.
        for i in range(count):
            field = field_locators.nth(i)
            # Optionally log the field's name or placeholder for debugging.
            field_name = await field.get_attribute("name") or await field.get_attribute("id") or f"field_{i}"
            print(f"Verifying field: {field_name}")
            await verify_field_default_state(page, field)

        print("✅ All Service Catalog form fields passed default state verification.")

        # Clean up.
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
