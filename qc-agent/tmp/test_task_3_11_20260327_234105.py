import asyncio
from playwright.async_api import async_playwright, expect

# Configuration
BASE_URL = "https://example.com"
LOGIN_URL = f"{BASE_URL}/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
USERNAME = "testuser@example.com"
PASSWORD = "Password123!"

# Selectors (adjust to match the actual application)
USERNAME_SELECTOR = "#username"
PASSWORD_SELECTOR = "#password"
LOGIN_BUTTON_SELECTOR = "#loginButton"
DASHBOARD_HEADER_SELECTOR = "h1.dashboard-title"

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to login page
        await page.goto(LOGIN_URL)
        await expect(page).to_have_url(LOGIN_URL)

        # 2. Enter credentials and submit
        await page.fill(USERNAME_SELECTOR, USERNAME)
        await page.fill(PASSWORD_SELECTOR, PASSWORD)
        await page.click(LOGIN_BUTTON_SELECTOR)

        # 3. Verify redirection to dashboard
        await expect(page).to_have_url(DASHBOARD_URL)
        await expect(page.locator(DASHBOARD_HEADER_SELECTOR)).to_be_visible()

        # 4. Refresh the page
        await page.reload()

        # 5. Verify dashboard still visible and user remains logged in
        await expect(page).to_have_url(DASHBOARD_URL)
        await expect(page.locator(DASHBOARD_HEADER_SELECTOR)).to_be_visible()

        # Optional: Verify session cookie exists
        cookies = await context.cookies()
        session_cookie = next((c for c in cookies if c['name'] == 'session_id'), None)
        assert session_cookie is not None, "Session cookie not found after refresh"

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())