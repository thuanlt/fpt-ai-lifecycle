import asyncio
from playwright.async_api import async_playwright

async def test_login_ui():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # TODO: Replace with the actual login page URL
        await page.goto("https://your-application-domain.com/login")

        # Verify page title "Login" is displayed at the top center
        title_locator = page.locator("h1, h2, h3, h4, h5, h6")
        title_text = await title_locator.first.text_content()
        assert title_text and title_text.strip() == "Login", f"Expected page title 'Login', got '{title_text}'"

        # Verify the username input field is visible with placeholder "Enter email"
        username_input = page.locator('input[placeholder="Enter email"]')
        assert await username_input.is_visible(), "Username input field is not visible"

        # Verify the password input field is visible with placeholder "Enter password"
        password_input = page.locator('input[placeholder="Enter password"]')
        assert await password_input.is_visible(), "Password input field is not visible"

        # Verify the "Sign In" button is visible and enabled
        sign_in_button = page.locator('button:has-text("Sign In")')
        assert await sign_in_button.is_visible(), "'Sign In' button is not visible"
        assert await sign_in_button.is_enabled(), "'Sign In' button is not enabled"

        # Verify a "Forgot Password?" link is displayed below the password field
        forgot_link = page.locator('text="Forgot Password?"')
        assert await forgot_link.is_visible(), "'Forgot Password?' link is not visible"

        await browser.close()

asyncio.run(test_login_ui())