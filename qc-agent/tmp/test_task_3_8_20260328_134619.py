import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to login page
        await page.goto("https://example.com/login")
        # Fill credentials
        await page.fill('input[name="username"]', "valid_user")
        await page.fill('input[name="password"]', "ValidPass123")
        # Check Remember Me
        await page.check('input[id="rememberMe"]')
        # Submit
        await page.click('button[type="submit"]')
        # Wait for navigation to dashboard
        await page.wait_for_url("**/dashboard")
        # Verify authentication success
        assert "Dashboard" in await page.title()
        # Verify persistent session cookie is set
        cookies = await context.cookies()
        session_cookie = next((c for c in cookies if c["name"] == "session"), None)
        assert session_cookie is not None, "Session cookie not found"
        await browser.close()

asyncio.run(run())