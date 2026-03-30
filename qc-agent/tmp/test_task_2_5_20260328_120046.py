import asyncio
from playwright.async_api import async_playwright, expect

# Constants – adjust these values to match the actual application under test
BASE_URL = "https://your-application-domain.com/service-registry/instances/create"
INSTANCE_NAME_SELECTOR = "#instance-name"          # CSS selector for the Instance Name input field
SAVE_BUTTON_SELECTOR = "#save-button"            # CSS selector for the Save button
ERROR_MESSAGE_SELECTOR = "#instance-name-error"   # CSS selector for the validation error message
MAX_LENGTH = 255

async def run_test():
    async with async_playwright() as p:
        # Launch a new browser context (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Create Service Instance page
        await page.goto(BASE_URL)

        # Generate a string that exceeds the maximum allowed length by 1 character
        over_length_name = "A" * (MAX_LENGTH + 1)

        # Fill the Instance Name field with the over‑length string
        await page.fill(INSTANCE_NAME_SELECTOR, over_length_name)

        # Click the Save button to trigger validation
        await page.click(SAVE_BUTTON_SELECTOR)

        # Wait for the validation error element to become visible
        error_element = page.locator(ERROR_MESSAGE_SELECTOR)
        await expect(error_element).to_be_visible(timeout=5000)

        # Verify the error message text matches the expected content
        expected_error_text = f"Maximum length exceeded ({MAX_LENGTH} characters)"
        await expect(error_element).to_have_text(expected_error_text)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
