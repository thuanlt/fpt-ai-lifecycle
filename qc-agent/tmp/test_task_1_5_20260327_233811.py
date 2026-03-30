import asyncio
from playwright.async_api import async_playwright

async def run_test():
    # URL of the login page – replace with the actual URL
    LOGIN_URL = "https://example.com/login"

    # List to collect console messages
    console_messages = []

    async with async_playwright() as p:
        # Launch Chrome (Chromium) browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console messages
        page.on("console", lambda msg: console_messages.append(msg))

        # Navigate to the login page
        await page.goto(LOGIN_URL, wait_until="load")

        # Basic UI/UX checks
        # 1. Verify the page title contains "Login"
        title = await page.title()
        assert "Login" in title, f"Page title does not contain 'Login': {title}"

        # 2. Verify the login form is visible
        login_form_selector = "form#loginForm"  # Adjust selector as needed
        assert await page.is_visible(login_form_selector), "Login form is not visible"

        # 3. Verify no console errors were logged
        error_messages = [msg.text for msg in console_messages if msg.type == "error"]
        assert not error_messages, f"Console errors found: {error_messages}"

        print("Test passed: Login page renders correctly with no console errors.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())