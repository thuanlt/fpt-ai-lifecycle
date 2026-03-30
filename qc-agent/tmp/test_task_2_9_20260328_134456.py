import asyncio
from playwright.async_api import async_playwright, expect

# Configuration
LOGIN_URL = "https://example.com/login"  # Replace with actual login page URL
USERNAME_SELECTOR = "#username"
PASSWORD_SELECTOR = "#password"
LOGIN_BUTTON_SELECTOR = "#loginBtn"
ERROR_MESSAGE_SELECTOR = ".error-message"

VALID_USERNAME = "valid_user"
VALID_PASSWORD = "CorrectPassword123"
INVALID_PASSWORD = "WrongPass!"
MAX_ATTEMPTS = 5

async def attempt_login(page, username, password):
    await page.fill(USERNAME_SELECTOR, username)
    await page.fill(PASSWORD_SELECTOR, password)
    await page.click(LOGIN_BUTTON_SELECTOR)
    # Wait for either navigation or error message
    try:
        await page.wait_for_selector(ERROR_MESSAGE_SELECTOR, timeout=3000)
    except Exception:
        # No error message appeared within timeout – could be successful navigation
        pass
    return await page.query_selector(ERROR_MESSAGE_SELECTOR)

async def verify_account_lockout():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(LOGIN_URL)

        # Perform MAX_ATTEMPTS failed login attempts
        for attempt in range(1, MAX_ATTEMPTS + 1):
            error_elem = await attempt_login(page, VALID_USERNAME, INVALID_PASSWORD)
            assert error_elem is not None, f"Expected error message on attempt {attempt}, but none was found."
            error_text = await error_elem.text_content()
            expected_msg = "Invalid username or password."
            assert expected_msg in error_text, f"Unexpected error message on attempt {attempt}: '{error_text}'"
            # Clear fields for next attempt
            await page.fill(USERNAME_SELECTOR, "")
            await page.fill(PASSWORD_SELECTOR, "")

        # After the fifth failed attempt, the system should lock the account
        # Verify lockout message appears
        lockout_error_elem = await attempt_login(page, VALID_USERNAME, INVALID_PASSWORD)
        assert lockout_error_elem is not None, "Lockout error message was not displayed after maximum failed attempts."
        lockout_text = await lockout_error_elem.text_content()
        expected_lockout_msg = "Account locked due to multiple failed login attempts. Try again later."
        assert expected_lockout_msg in lockout_text, f"Lockout message mismatch. Got: '{lockout_text}'"

        # Attempt login with correct credentials while account is locked
        success_error_elem = await attempt_login(page, VALID_USERNAME, VALID_PASSWORD)
        assert success_error_elem is not None, "Expected lockout message on correct credentials, but none was shown."
        success_error_text = await success_error_elem.text_content()
        assert expected_lockout_msg in success_error_text, f"Account should remain locked; got: '{success_error_text}'"

        # Verify that no session token (e.g., auth cookie) is set
        cookies = await context.cookies()
        auth_cookies = [c for c in cookies if c.name.lower().startswith("auth") or "session" in c.name.lower()]
        assert len(auth_cookies) == 0, f"Session token was issued despite account lockout: {auth_cookies}"

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_account_lockout())
