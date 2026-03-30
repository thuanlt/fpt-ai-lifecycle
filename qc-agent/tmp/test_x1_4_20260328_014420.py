import asyncio
from playwright.async_api import async_playwright, expect

# Replace these with valid credentials for the application under test
VALID_EMAIL = "test.user@example.com"
VALID_PASSWORD = "CorrectPassword123"

async def test_successful_login():
    async with async_playwright() as p:
        # Launch browser (headless mode). Change to "chromium", "firefox", or "webkit" as needed.
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page – replace with the actual URL of the application.
        await page.goto("https://your-app-domain.com/login")

        # Fill in the email field – adjust selector according to the actual DOM.
        await page.fill('input[name="email"]', VALID_EMAIL)
        # Fill in the password field.
        await page.fill('input[name="password"]', VALID_PASSWORD)
        # Click the Sign In button – assuming the button contains the exact text "Sign In".
        await page.click('button:has-text("Sign In")')

        # Wait for navigation to the dashboard/home page.
        await page.wait_for_load_state('networkidle')

        # Verify that the user is redirected to the dashboard/home page.
        # This can be done by checking the URL or a unique element on the landing page.
        expect(page).to_have_url(lambda url: "dashboard" in url or "home" in url)

        # Verify the welcome message is displayed.
        welcome_locator = page.locator('text=Welcome,')
        await expect(welcome_locator).to_be_visible()
        # Optionally, verify the user name appears in the welcome message.
        await expect(welcome_locator).to_contain_text("Welcome, ")

        # Verify that an authentication token is stored in a secure HttpOnly cookie.
        cookies = await context.cookies()
        auth_cookie = next((c for c in cookies if c['name'].lower() in ["auth", "session", "token"]), None)
        if auth_cookie:
            assert auth_cookie["httpOnly"], "Authentication cookie should be HttpOnly"
        else:
            raise AssertionError("Authentication cookie not found after login")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_successful_login())
