import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these selectors according to the actual application under test
USERNAME_SELECTOR = "input[name='username']"
PASSWORD_SELECTOR = "input[name='password']"
SUBMIT_BUTTON_SELECTOR = "button[type='submit']"
VALIDATION_MESSAGE_SELECTOR = "//div[contains(@class, 'validation') and contains(text(), 'Username is required')]"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page – replace with the actual URL
        await page.goto("https://example.com/login")

        # Ensure the username field is empty (explicitly clear it)
        await page.fill(USERNAME_SELECTOR, "")
        # Fill a valid password – replace with a known valid password if needed
        await page.fill(PASSWORD_SELECTOR, "ValidPassword123!")
        # Click the submit button
        await page.click(SUBMIT_BUTTON_SELECTOR)

        # Verify the inline validation message for missing username appears
        validation_locator = page.locator(VALIDATION_MESSAGE_SELECTOR)
        await expect(validation_locator).to_be_visible(timeout=5000)
        await expect(validation_locator).to_have_text("Username is required")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
