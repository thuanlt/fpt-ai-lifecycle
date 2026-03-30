import asyncio
from playwright.async_api import async_playwright

# Configuration
LOGIN_URL = "https://example.com/login"
DASHBOARD_URL = "https://example.com/dashboard"
VALID_USERNAME = "testuser"
VALID_PASSWORD = "Password123!"

# Selectors
USERNAME_SELECTOR = "#username"
PASSWORD_SELECTOR = "#password"
LOGIN_BUTTON_SELECTOR = "#loginButton"
LOGOUT_BUTTON_SELECTOR = "#logoutButton"
TOAST_SELECTOR = ".toast"
SESSION_COOKIE_NAME = "session"  # Adjust if your app uses a different cookie name

async def test_logout_clears_session():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to login page
        await page.goto(LOGIN_URL)

        # 2. Enter valid credentials and submit
        await page.fill(USERNAME_SELECTOR, VALID_USERNAME)
        await page.fill(PASSWORD_SELECTOR, VALID_PASSWORD)
        await page.click(LOGIN_BUTTON_SELECTOR)

        # 3. Verify redirection to dashboard
        await page.wait_for_url(DASHBOARD_URL, timeout=5000)
        assert DASHBOARD_URL in page.url, f"Expected to be on dashboard, but on {page.url}"

        # 4. Click logout button
        await page.click(LOGOUT_BUTTON_SELECTOR)

        # 5. Verify redirection back to login page
        await page.wait_for_url(LOGIN_URL, timeout=5000)
        assert LOGIN_URL in page.url, f"Expected to be on login page, but on {page.url}"

        # 6. Verify session cookie is cleared
        cookies = await context.cookies()
        session_cookies = [c for c in cookies if c.get("name") == SESSION_COOKIE_NAME]
        assert not session_cookies, "Session cookie still present after logout"

        # 7. Verify toast message appears
        await page.wait_for_selector(TOAST_SELECTOR, timeout=5000)
        toast_text = await page.inner_text(TOAST_SELECTOR)
        assert "Logged out" in toast_text, f"Expected 'Logged out' toast, got '{toast_text}'"

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_logout_clears_session())
