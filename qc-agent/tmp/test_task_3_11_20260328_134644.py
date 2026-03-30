import asyncio
from playwright.async_api import async_playwright

async def test_login_with_email():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")
        # Enter a registered email address in the username field
        await page.fill('input[name="username"]', "user@example.com")
        # Enter the correct password
        await page.fill('input[name="password"]', "CorrectPassword123")
        # Click the submit button
        await page.click('button[type="submit"]')
        # Wait for navigation / network idle to ensure page transition
        await page.wait_for_load_state('networkidle')
        # Verify that the dashboard page is loaded
        assert "dashboard" in page.url.lower(), "Dashboard page not loaded"
        # Optionally verify a dashboard-specific element
        await page.wait_for_selector("text=Dashboard", timeout=5000)
        print("Login with email successful – dashboard loaded.")
        await browser.close()

asyncio.run(test_login_with_email())
