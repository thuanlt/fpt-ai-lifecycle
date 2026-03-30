import asyncio
from playwright.async_api import async_playwright, expect

# -----------------------------------------------------------------------------
# Configuration – adjust these selectors / URLs according to the actual app
# -----------------------------------------------------------------------------
BASE_URL = "https://your-application-url.com"  # TODO: replace with actual base URL
SERVICE_NAME = "Basic Hosting"
NEW_DESCRIPTION = "Updated description for Basic Hosting service"

# Selectors (CSS/XPath) – these are placeholders and should be updated to match the UI
SELECTORS = {
    "service_row": f"//tr[td[contains(text(), '{SERVICE_NAME}')]]",
    "edit_icon": "button[data-test-id='edit-service']",  # inside the service row
    "edit_form": "form[data-test-id='service-edit-form']",
    "description_input": "textarea[name='description']",
    "save_button": "button[type='submit']",
    "success_toast": "div[data-test-id='toast-success']",
    "close_form_button": "button[data-test-id='close-edit-form']",
}

async def edit_service_and_verify(page):
    # 1. Navigate to Service Catalog page
    await page.goto(f"{BASE_URL}/service-catalog")
    await page.wait_for_load_state("networkidle")

    # 2. Locate the service row for the target service
    service_row = page.locator(SELECTORS["service_row"])
    await expect(service_row).to_be_visible(timeout=5000)

    # 3. Click the Edit icon/button for that service
    edit_button = service_row.locator(SELECTORS["edit_icon"])
    await edit_button.click()

    # 4. Verify the edit form appears and is pre‑populated
    edit_form = page.locator(SELECTORS["edit_form"])
    await expect(edit_form).to_be_visible(timeout=5000)
    description_input = edit_form.locator(SELECTORS["description_input"])
    await expect(description_input).to_have_value()  # value should exist (pre‑populated)

    # 5. Change the description field
    await description_input.fill(NEW_DESCRIPTION)

    # 6. Click Save
    await edit_form.locator(SELECTORS["save_button"]).click()

    # 7. Verify success toast/message appears
    success_toast = page.locator(SELECTORS["success_toast"])
    await expect(success_toast).to_contain_text("Service updated successfully", timeout=5000)

    # 8. Verify the edit form closes (or is no longer visible)
    await expect(edit_form).to_be_hidden(timeout=5000)

    # 9. Re‑open the edit form for the same service to verify persistence
    await edit_button.click()
    await expect(edit_form).to_be_visible(timeout=5000)
    description_input = edit_form.locator(SELECTORS["description_input"])
    await expect(description_input).to_have_value(NEW_DESCRIPTION)

    # Optional: close the form at the end of the test
    await edit_form.locator(SELECTORS["close_form_button"]).click()
    await expect(edit_form).to_be_hidden(timeout=5000)

async def run_test():
    async with async_playwright() as p:
        # Choose the browser you need – here we use Chromium headless
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await edit_service_and_verify(page)
            print("✅ Test completed successfully")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
