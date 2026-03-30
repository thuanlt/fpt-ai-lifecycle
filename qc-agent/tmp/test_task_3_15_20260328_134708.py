import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser (set headless=False for visual debugging, change to True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Step 1: Navigate to the login page
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")

        # ------------------------------------------------------------
        # Step 2: Perform a successful login
        # ------------------------------------------------------------
        await page.fill("#username", "valid_user")
        await page.fill("#password", "valid_password")
        await page.click("#loginButton")
        # Wait for an element that indicates a successful login (e.g., dashboard)
        await page.wait_for_selector("#dashboard", timeout=10000)

        # ------------------------------------------------------------
        # Step 3: Remain idle for the configured session timeout (15 minutes)
        # ------------------------------------------------------------
        await page.wait_for_timeout(15 * 60 * 1000)  # 15 minutes expressed in milliseconds

        # ------------------------------------------------------------
        # Step 4: Verify that the session has expired
        # ------------------------------------------------------------
        # Expect the browser to be redirected back to the login page
        await page.wait_for_url("**/login", timeout=10000)
        # Verify that a timeout notification is shown to the user
        await page.wait_for_selector(".notification:has-text('Session timed out')", timeout=5000)

        # Clean up
        await browser.close()

asyncio.run(main())
