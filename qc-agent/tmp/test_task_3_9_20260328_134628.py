import asyncio
from playwright.async_api import async_playwright, expect

# Configuration - replace with actual values for your application
LOGIN_URL = "https://example.com/login"
USERNAME = "test_user"
PASSWORD = "test_password"

# Selectors - update these to match the real DOM elements
USERNAME_SELECTOR = "#username"
PASSWORD_SELECTOR = "#password"
LOGIN_BUTTON_SELECTOR = "text=Login"
DASHBOARD_SELECTOR = "#dashboard"  # An element that only appears on the dashboard
USER_MENU_SELECTOR = "#user-menu"   # The element that opens the user menu
LOGOUT_BUTTON_SELECTOR = "text=Logout"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to the login page
        await page.goto(LOGIN_URL)

        # 2. Perform a successful login
        await page.fill(USERNAME_SELECTOR, USERNAME)
        await page.fill(PASSWORD_SELECTOR, PASSWORD)
        await page.click(LOGIN_BUTTON_SELECTOR)

        # 3. Verify that the dashboard is displayed
        await page.wait_for_selector(DASHBOARD_SELECTOR, timeout=5000)
        dashboard_visible = await page.is_visible(DASHBOARD_SELECTOR)
        assert dashboard_visible, "Dashboard should be visible after successful login"

        # 4. Open the user menu and click the Logout button
        await page.click(USER_MENU_SELECTOR)
        await page.click(LOGOUT_BUTTON_SELECTOR)

        # 5. Verify that the session is terminated and user is redirected to the login page
        await page.wait_for_url(LOGIN_URL, timeout=5000)
        current_url = page.url
        assert LOGIN_URL in current_url, f"User should be redirected to login page, got {current_url}"

        # 6. Verify that the login form is cleared
        username_value = await page.input_value(USERNAME_SELECTOR)
        password_value = await page.input_value(PASSWORD_SELECTOR)
        assert username_value == "", "Username field should be cleared after logout"
        assert password_value == "", "Password field should be cleared after logout"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
