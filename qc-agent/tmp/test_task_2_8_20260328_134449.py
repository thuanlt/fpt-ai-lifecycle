import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – adjust these values to match the application under test
# ---------------------------------------------------------------------------
LOGIN_URL = "https://example.com/login"  # <-- replace with actual login page URL
USERNAME_SELECTOR = "#username"          # <-- CSS selector for the email/username field
PASSWORD_SELECTOR = "#password"          # <-- CSS selector for the password field
LOGIN_BUTTON_SELECTOR = "#loginButton"   # <-- CSS selector for the login button
ERROR_MESSAGE_SELECTOR = "#errorMessage" # <-- CSS selector where the error text appears
EXPECTED_ERROR_TEXT = "Invalid credentials"

async def test_login_with_nonexistent_account(page):
    """Verify login fails with a well‑formed but unregistered account.

    Steps:
    1. Navigate to the login page.
    2. Fill the username field with a valid‑format email that does not exist.
    3. Fill the password field with any value.
    4. Click the Login button.
    5. Assert that the server returns the expected error message and no session is created.
    """
    # 1. Go to login page
    await page.goto(LOGIN_URL)

    # 2. Enter a well‑formed but unregistered email/username
    await page.fill(USERNAME_SELECTOR, "nonexistent_user@example.com")

    # 3. Enter any password
    await page.fill(PASSWORD_SELECTOR, "SomeRandomPassword123!")

    # 4. Click Login
    await page.click(LOGIN_BUTTON_SELECTOR)

    # 5. Verify error message is displayed
    error_element = page.locator(ERROR_MESSAGE_SELECTOR)
    await expect(error_element).to_be_visible()
    await expect(error_element).to_have_text(EXPECTED_ERROR_TEXT)

    # Additional check: ensure no authenticated session cookie is set (example cookie name)
    # Adjust "session_id" to the actual auth cookie name used by the application.
    cookies = await page.context.cookies()
    session_cookies = [c for c in cookies if c['name'] == 'session_id']
    assert len(session_cookies) == 0, "Session cookie should not be created for invalid login"

async def main():
    async with async_playwright() as p:
        # Choose the browser you prefer (chromium, firefox, webkit)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await test_login_with_nonexistent_account(page)
            print("✅ Test passed: login with nonexistent account correctly rejected.")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
