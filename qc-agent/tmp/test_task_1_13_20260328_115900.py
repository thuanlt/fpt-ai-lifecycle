import asyncio
from playwright.async_api import async_playwright, expect

# Configuration – adjust these values to match your environment
APP_URL = "https://your-app-domain.com/login"
USERNAME = "test_user"
PASSWORD = "test_password"
SERVICE_NAME = "Sample Service"  # The name of the service that is initially in "Active" state

async def login(page):
    """Perform login – replace selectors with actual ones for your app."""
    await page.goto(APP_URL)
    await page.fill("input[name='username']", USERNAME)
    await page.fill("input[name='password']", PASSWORD)
    await page.click("button:has-text('Login')")
    # Wait for navigation to dashboard or service list page
    await page.wait_for_load_state('networkidle')

async def change_service_status_to_retired(page):
    """Test case: Change service status from Active to Retired and verify UI behavior."""
    # 1. Navigate to Service Management page
    await page.click("nav >> text=Service Management")
    await page.wait_for_selector("h1:has-text('Service Management')")

    # 2. Locate the service that is currently Active
    # Assuming each row has data-service-name and data-status attributes
    service_row_selector = f"tr[data-service-name='{SERVICE_NAME}'][data-status='Active']"
    await page.wait_for_selector(service_row_selector)

    # 3. Open the edit dialog for the selected service
    await page.click(f"{service_row_selector} >> button:has-text('Edit')")
    await page.wait_for_selector("dialog[role='dialog']")

    # 4. Change status from Active to Retired
    await page.select_option("select[name='status']", label="Retired")

    # 5. Save the changes
    await page.click("dialog >> button:has-text('Save')")

    # 6. Verify that the status change was successful
    # Wait for the row to be updated (could be a toast or table refresh)
    await page.wait_for_selector(f"{service_row_selector} >> text=Retired")
    status_cell = await page.locator(f"{service_row_selector} td[data-field='status']")
    await expect(status_cell).to_have_text("Retired")

    # 7. Verify that the service row is now read‑only (Edit button disabled)
    edit_button = await page.locator(f"{service_row_selector} >> button:has-text('Edit')")
    await expect(edit_button).to_be_disabled()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await login(page)
            await change_service_status_to_retired(page)
            print("✅ Test case passed: Service status transitioned from Active to Retired and UI reflects read‑only state.")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
