import asyncio
from playwright.async_api import async_playwright, expect

LOGIN_URL = "https://example.com/login"

async def test_login_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Step 1: Navigate to the login page URL
        await page.goto(LOGIN_URL)
        # Expected: Login form is displayed
        login_form = page.locator("form#loginForm")
        await expect(login_form).to_be_visible()

        # Step 2: Observe the username field, password field, submit button,
        # "Remember Me" checkbox, and "Forgot Password" link
        username = page.locator('input[name="username"]')
        password = page.locator('input[name="password"]')
        submit = page.locator('button[type="submit"]')
        remember = page.locator('input[type="checkbox"][name="remember"]')
        forgot = page.locator('a[href*="forgot"]')

        await expect(username).to_be_visible()
        await expect(username).to_be_enabled()
        await expect(password).to_be_visible()
        await expect(password).to_be_enabled()
        await expect(submit).to_be_visible()
        await expect(submit).to_be_enabled()
        await expect(remember).to_be_visible()
        await expect(remember).to_be_enabled()
        await expect(forgot).to_be_visible()

        await browser.close()

asyncio.run(test_login_form())