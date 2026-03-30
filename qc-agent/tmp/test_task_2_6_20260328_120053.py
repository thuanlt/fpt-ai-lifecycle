import asyncio
from playwright.async_api import async_playwright, Page, expect

# Adjust these constants to match the actual application under test
BASE_URL = "http://localhost:3000"  # Replace with the real URL of the Service Registry UI
VERSION_INPUT_SELECTOR = "#version-input"   # CSS selector for the version input field
SAVE_BUTTON_SELECTOR = "#save-button"       # CSS selector for the Save/Create button
ERROR_MESSAGE_SELECTOR = ".error-message"   # CSS selector for the validation error element

async def validate_semantic_version_error(page: Page) -> None:
    """Test that entering an invalid version string shows the correct validation error.

    Steps:
    1. Navigate to the Service Registry > Instance Management page.
    2. Click the button/link that opens the "Create Service Instance" dialog/form.
    3. Fill the version input with an invalid value ("v1").
    4. Click the Save button.
    5. Verify that the expected validation error is displayed.
    """
    # 1. Go to the Instance Management page
    await page.goto(f"{BASE_URL}/service-registry/instances")

    # 2. Open the Create Service Instance UI (adjust selector as needed)
    # Assuming there is a button with id "create-instance" that opens the form
    await page.click("#create-instance")

    # 3. Enter invalid version string
    await page.fill(VERSION_INPUT_SELECTOR, "v1")

    # 4. Click Save
    await page.click(SAVE_BUTTON_SELECTOR)

    # 5. Verify validation error
    error_locator = page.locator(ERROR_MESSAGE_SELECTOR)
    await expect(error_locator).to_be_visible()
    await expect(error_locator).to_have_text(
        "Version must follow semantic versioning (MAJOR.MINOR.PATCH)"
    )

async def run_test() -> None:
    async with async_playwright() as p:
        # Choose the browser you prefer; here we use Chromium in headed mode for visibility
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await validate_semantic_version_error(page)
            print("✅ Test passed: Validation error displayed as expected.")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
