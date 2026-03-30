import asyncio
from playwright.async_api import async_playwright, expect

# Replace this URL with the actual page URL where the Create User form is located
CREATE_USER_URL = "http://example.com/create-user"

# Selectors – adjust these to match the actual application's DOM
USERNAME_INPUT = "input[name='username']"
EMAIL_INPUT = "input[name='email']"
PASSWORD_INPUT = "input[name='password']"
SAVE_BUTTON = "button:has-text('Save')"
PASSWORD_ERROR = "text=Password must be at least 8 characters"

async def run_test():
    async with async_playwright() as p:
        # Launch a headless Chromium browser; set headless=False for debugging
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Create User form page
        await page.goto(CREATE_USER_URL)

        # --- Step 1: Fill out the form with valid data except for a short password ---
        await page.fill(USERNAME_INPUT, "testuser")
        await page.fill(EMAIL_INPUT, "testuser@example.com")
        # Password shorter than 8 characters to trigger validation
        await page.fill(PASSWORD_INPUT, "short")

        # --- Step 2: Click the Save button ---
        await page.click(SAVE_BUTTON)

        # --- Expected Result 1: Inline error message appears ---
        error_locator = page.locator(PASSWORD_ERROR)
        await expect(error_locator).to_be_visible()
        await expect(error_locator).to_have_text("Password must be at least 8 characters")

        # --- Expected Result 2: Save button remains disabled ---
        save_button_locator = page.locator(SAVE_BUTTON)
        await expect(save_button_locator).to_be_disabled()

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
