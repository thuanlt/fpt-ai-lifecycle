import asyncio
from playwright.async_api import async_playwright, expect

# Adjust this URL to point to the application under test
BASE_URL = "http://localhost:3000"

async def test_service_creation_form_layout():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Management page (adjust path if needed)
        await page.goto(f"{BASE_URL}/service-management")

        # 1. Click "Add Service" button
        add_service_button = page.get_by_role("button", name="Add Service")
        await expect(add_service_button).to_be_visible()
        await add_service_button.click()

        # Verify Service creation modal appears
        modal = page.get_by_role("dialog")
        await expect(modal).to_be_visible()

        # Verify modal title reads "Create New Service"
        modal_title = modal.get_by_role("heading", name="Create New Service")
        await expect(modal_title).to_be_visible()

        # Verify all input fields are visible
        name_input = modal.get_by_label("Name")
        description_input = modal.get_by_label("Description")
        version_input = modal.get_by_label("Version")
        status_select = modal.get_by_label("Status")

        await expect(name_input).to_be_visible()
        await expect(description_input).to_be_visible()
        await expect(version_input).to_be_visible()
        await expect(status_select).to_be_visible()

        # Verify "Save" and "Cancel" buttons are enabled
        save_button = modal.get_by_role("button", name="Save")
        cancel_button = modal.get_by_role("button", name="Cancel")
        await expect(save_button).to_be_enabled()
        await expect(cancel_button).to_be_enabled()

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_service_creation_form_layout())
