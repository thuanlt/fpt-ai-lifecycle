import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match your environment
SERVICE_URL = "http://localhost:3000/service-management"
SERVICE_NAME = "Test Service"

async def test_incremental_version_update(page):
    # Navigate to Service Management page
    await page.goto(SERVICE_URL)

    # Search and select the service to edit
    await page.fill("input[placeholder='Search services']", SERVICE_NAME)
    await page.click(f"text={SERVICE_NAME}")

    # Click the Edit button for the selected service
    await page.click("button:has-text('Edit')")

    # Verify the current version is 1.0.0
    current_version = await page.input_value("input[name='version']")
    assert current_version == "1.0.0", f"Expected version 1.0.0, got {current_version}"

    # Update the version to 1.1.0
    await page.fill("input[name='version']", "1.1.0")
    await page.click("button:has-text('Save')")

    # Wait for a success notification that the update succeeded
    await expect(page.locator("text=Update succeeds")).to_be_visible(timeout=5000)

    # Verify the service now shows version 1.1.0 in the list/detail view
    await page.wait_for_selector(f"text={SERVICE_NAME}")
    displayed_version = await page.text_content(f"tr:has-text('{SERVICE_NAME}') >> td.version")
    assert displayed_version == "1.1.0", f"Version not updated in UI, found {displayed_version}"

    # Open the change‑history panel and verify the version bump entry is recorded
    await page.click("button:has-text('Change History')")
    history_entry = await page.text_content("table.history >> tr:first-child >> td")
    assert "Version changed from 1.0.0 to 1.1.0" in history_entry, "Version bump not recorded in history"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await test_incremental_version_update(page)
            print("Test passed")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
