import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match the actual application under test
URL = "https://your-application-domain.com/service-catalog"  # TODO: replace with real URL
OWNER_EMAIL_SELECTOR = "input[name='ownerEmail']"  # TODO: verify the selector for Owner Email field
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"  # TODO: verify the selector for the Save button
ERROR_MESSAGE_SELECTOR = "text=Owner Email is required"  # Generic selector for required error
INVALID_FORMAT_MESSAGE_SELECTOR = "text=Enter a valid email address"  # Generic selector for format error

async def verify_owner_email_validation(page):
    # 1. Navigate to the Service Catalog Management page
    await page.goto(URL)
    await page.wait_for_load_state("networkidle")

    # ---------------------------------------------------------------------
    # Scenario 1: Owner Email left blank – expect required field validation
    # ---------------------------------------------------------------------
    # Ensure the field is empty (clear any pre‑filled value)
    await page.fill(OWNER_EMAIL_SELECTOR, "")
    # Click the Save button
    await page.click(SAVE_BUTTON_SELECTOR)
    # Verify the required error message is displayed
    error_msg = page.locator(ERROR_MESSAGE_SELECTOR)
    await expect(error_msg).to_be_visible()
    # Optionally, ensure the form is not submitted (e.g., URL does not change)
    # ---------------------------------------------------------------------
    # Scenario 2: Invalid email format – expect format validation message
    # ---------------------------------------------------------------------
    await page.fill(OWNER_EMAIL_SELECTOR, "invalid-email")
    await page.click(SAVE_BUTTON_SELECTOR)
    # Verify the format error message is displayed
    format_msg = page.locator(INVALID_FORMAT_MESSAGE_SELECTOR)
    await expect(format_msg).to_be_visible()

async def run():
    async with async_playwright() as p:
        # Choose the browser you prefer (chromium, firefox, webkit)
        browser = await p.chromium.launch(headless=False)  # set headless=True for CI
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await verify_owner_email_validation(page)
            print("✅ Owner Email validation test passed")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
