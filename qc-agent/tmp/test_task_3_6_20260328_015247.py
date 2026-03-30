import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match your application under test
BASE_URL = "http://localhost:3000"  # Replace with actual URL of the Service Catalog app
CREATE_BUTTON_SELECTOR = "text=Create New Service"  # Button to open the create form
FORM_SELECTOR = "form#service-create-form"  # The create service form
NAME_INPUT_SELECTOR = "input[name='name']"
CATEGORY_DROPDOWN_SELECTOR = "select[name='category']"
DESCRIPTION_TEXTAREA_SELECTOR = "textarea[name='description']"
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"
SUCCESS_TOAST_SELECTOR = "text=Service saved successfully"
SERVICE_LIST_ROW_SELECTOR = "tr[data-service-name='Premium Consulting']"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Open the Service Catalog page
        await page.goto(BASE_URL)
        # Wait for the page to load – adjust selector as needed for a stable element
        await page.wait_for_selector(CREATE_BUTTON_SELECTOR)

        # 2. Open the "Create New Service" form
        await page.click(CREATE_BUTTON_SELECTOR)
        await page.wait_for_selector(FORM_SELECTOR)
        # Verify form is displayed
        form = page.locator(FORM_SELECTOR)
        expect(form).to_be_visible()

        # 3. Fill in the form fields
        await page.fill(NAME_INPUT_SELECTOR, "Premium Consulting")
        await page.select_option(CATEGORY_DROPDOWN_SELECTOR, label="Consulting")
        await page.fill(DESCRIPTION_TEXTAREA_SELECTOR, "High‑end consulting services for enterprise clients.")

        # Verify inputs accepted the values
        expect(page.locator(NAME_INPUT_SELECTOR)).to_have_value("Premium Consulting")
        expect(page.locator(CATEGORY_DROPDOWN_SELECTOR)).to_have_value(await page.eval_on_selector(CATEGORY_DROPDOWN_SELECTOR, "el => el.value"))
        expect(page.locator(DESCRIPTION_TEXTAREA_SELECTOR)).to_have_value("High‑end consulting services for enterprise clients.")

        # 4. Click "Save"
        await page.click(SAVE_BUTTON_SELECTOR)

        # 5. Verify success toast/message appears
        await page.wait_for_selector(SUCCESS_TOAST_SELECTOR, timeout=5000)
        expect(page.locator(SUCCESS_TOAST_SELECTOR)).to_be_visible()

        # 6. Verify the form closes and we return to the Service Catalog list
        # Assuming the form disappears after save
        await expect(page.locator(FORM_SELECTOR)).to_be_hidden()

        # 7. Locate the newly created service in the list
        await page.wait_for_selector(SERVICE_LIST_ROW_SELECTOR, timeout=5000)
        service_row = page.locator(SERVICE_LIST_ROW_SELECTOR)
        expect(service_row).to_be_visible()
        # Verify displayed details (name, category, status) – adjust selectors as needed
        expect(service_row.locator("td[data-field='name']")).to_have_text("Premium Consulting")
        expect(service_row.locator("td[data-field='category']")).to_have_text("Consulting")
        # Assuming a default status column exists, e.g., "Active"
        expect(service_row.locator("td[data-field='status']")).to_have_text("Active")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
