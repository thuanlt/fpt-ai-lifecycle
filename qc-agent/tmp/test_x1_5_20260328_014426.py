import asyncio
from playwright.async_api import async_playwright, expect

# Configuration - adjust these values to match your application
BASE_URL = "https://your-app.example.com/login"  # URL of the login page
REGISTERED_EMAIL = "test.user@example.com"
WRONG_PASSWORD = "incorrectPassword123"
EXPECTED_ERROR_MESSAGE = "Incorrect email or password"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to the login page
        await page.goto(BASE_URL)

        # 2. Fill in a registered email
        await page.fill('input[name="email"]', REGISTERED_EMAIL)

        # 3. Fill in an incorrect password
        await page.fill('input[name="password"]', WRONG_PASSWORD)

        # 4. Click the "Sign In" button
        # Adjust selector if your button uses a different attribute or text
        await page.click('button:has-text("Sign In")')

        # 5. Verify the error toast/message appears with the correct text
        # Assuming the toast has a role="alert" or a specific CSS class; adjust as needed
        error_locator = page.locator('role=alert')
        await expect(error_locator).to_be_visible(timeout=5000)
        await expect(error_locator).to_have_text(EXPECTED_ERROR_MESSAGE)

        # 6. Verify the user remains on the login page (URL unchanged)
        await expect(page).to_have_url(BASE_URL)

        # 7. Verify the input fields retain the entered values
        email_value = await page.input_value('input[name="email"]')
        password_value = await page.input_value('input[name="password"]')
        assert email_value == REGISTERED_EMAIL, f"Email field value changed: {email_value}"
        assert password_value == WRONG_PASSWORD, f"Password field value changed: {password_value}"

        # Cleanup
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
