import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # TODO: Replace the URL below with the actual login page URL.
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")

        valid_username = "testuser"
        wrong_password = "WrongPass123"

        # Perform five consecutive failed login attempts
        for attempt in range(1, 6):
            # Clear any previous input (optional, depends on app behavior)
            await page.fill("#username", "")
            await page.fill("#password", "")

            # Enter credentials
            await page.fill("#username", valid_username)
            await page.fill("#password", wrong_password)

            # Submit the login form
            await page.click("#loginButton")

            # Small pause to allow the server response to render
            await page.wait_for_timeout(1000)  # adjust timing as needed

        # ------------------------------------------------------------
        # Verification after the fifth attempt
        # ------------------------------------------------------------
        lockout_message_selector = "text=Account locked due to multiple failed login attempts"
        await page.wait_for_selector(lockout_message_selector, timeout=5000)
        lockout_element = await page.query_selector(lockout_message_selector)
        assert lockout_element is not None, "Lockout message was not displayed"
        print("✅ Test passed: Account lockout message displayed after five failed attempts.")

        await context.close()
        await browser.close()

asyncio.run(run_test())