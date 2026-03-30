import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match the actual application under test
BASE_URL = "https://your-application-url.com/create-user"  # URL of the Create User form page
EMAIL_SELECTOR = "#email"  # CSS selector for the Email input field
SAVE_BUTTON_SELECTOR = "#saveButton"  # CSS selector for the Save button
ERROR_MESSAGE_SELECTOR = "#email-error"  # CSS selector for the inline email validation error message

# Fill in other required fields with valid data – replace selectors as needed
OTHER_FIELDS = {
    "#firstName": "John",
    "#lastName": "Doe",
    "#username": "johndoe",
    # Add more field selectors/value pairs if the form requires them
}

async def run_test():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Create User form
        await page.goto(BASE_URL)

        # Populate required fields with valid data
        for selector, value in OTHER_FIELDS.items():
            await page.fill(selector, value)

        # Step 1: Enter an invalid email address
        await page.fill(EMAIL_SELECTOR, "invalid-email")

        # Attempt to click Save – the button should remain disabled, but we attempt the click to be safe
        # Verify that the Save button is disabled
        save_button = page.locator(SAVE_BUTTON_SELECTOR)
        await expect(save_button).to_be_disabled()

        # Verify that the inline validation error message appears with the correct text
        error_message = page.locator(ERROR_MESSAGE_SELECTOR)
        await expect(error_message).to_be_visible()
        await expect(error_message).to_have_text("Enter a valid email address")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
