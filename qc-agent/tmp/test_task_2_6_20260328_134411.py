import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match the actual application under test
LOGIN_URL = "http://example.com/login"  # <-- replace with real login page URL
USERNAME_SELECTOR = "input[name='username']"  # <-- replace with actual selector
PASSWORD_SELECTOR = "input[name='password']"  # <-- replace with actual selector
LOGIN_BUTTON_SELECTOR = "button[type='submit']"  # <-- replace with actual selector
VALIDATION_MESSAGE_SELECTOR = "text=Username may only contain alphanumeric characters"  # <-- replace with actual selector or text locator

async def test_invalid_username_characters():
    async with async_playwright() as p:
        # Launch browser (headless by default; set headless=False for debugging)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(LOGIN_URL)

        # Input invalid username and a valid password
        await page.fill(USERNAME_SELECTOR, "user name!")
        await page.fill(PASSWORD_SELECTOR, "ValidPassword123")

        # Click the login button
        await page.click(LOGIN_BUTTON_SELECTOR)

        # Assert that the validation message appears
        validation_message = page.locator(VALIDATION_MESSAGE_SELECTOR)
        await expect(validation_message).to_be_visible()

        # Optionally, ensure that no network request for authentication is sent
        # This can be verified by listening to request events before clicking
        # and asserting that no request matching the authentication endpoint occurs.

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_invalid_username_characters())
