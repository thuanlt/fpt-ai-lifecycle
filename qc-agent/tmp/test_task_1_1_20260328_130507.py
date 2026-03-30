import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless mode can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # ------------------------------------------------------------
        # 1. Verify the page loads and the company logo is displayed
        # ------------------------------------------------------------
        logo = page.locator("img[alt='Company Logo']")
        await expect(logo).to_be_visible()

        # ------------------------------------------------------------
        # 2. Verify Username/Email field and its label
        # ------------------------------------------------------------
        username_label = page.locator("label", has_text="Username or Email")
        await expect(username_label).to_be_visible()
        username_input = page.locator(
            "input[name='username'], input[id='username'], input[placeholder='Username or Email']"
        )
        await expect(username_input).to_be_visible()

        # ------------------------------------------------------------
        # 3. Verify Password field and its label
        # ------------------------------------------------------------
        password_label = page.locator("label", has_text="Password")
        await expect(password_label).to_be_visible()
        password_input = page.locator("input[type='password']")
        await expect(password_input).to_be_visible()

        # ------------------------------------------------------------
        # 4. Verify "Remember Me" checkbox and its label
        # ------------------------------------------------------------
        remember_checkbox = page.locator("input[type='checkbox'][name='remember']")
        await expect(remember_checkbox).to_be_visible()
        remember_label = page.locator("label", has_text="Remember Me")
        await expect(remember_label).to_be_visible()

        # ------------------------------------------------------------
        # 5. Verify the Login button is present and enabled
        # ------------------------------------------------------------
        login_button = page.locator("button:has-text('Login')")
        await expect(login_button).to_be_visible()
        await expect(login_button).to_be_enabled()

        # ------------------------------------------------------------
        # 6. Verify the "Forgot Password?" link is displayed
        # ------------------------------------------------------------
        forgot_link = page.locator("a:has-text('Forgot Password?')")
        await expect(forgot_link).to_be_visible()

        # Clean up
        await browser.close()

asyncio.run(run())
