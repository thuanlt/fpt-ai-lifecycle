import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch Chromium browser (headful for visual verification; set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        # Set desktop viewport size
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        # Navigate to the login page – replace with the actual URL if different
        await page.goto("http://localhost/login")

        # Locate the login button (assumes button text is exactly "Log In")
        login_button = page.locator("button:has-text('Log In')")
        # Verify button is visible
        await expect(login_button).to_be_visible()
        # Verify button label reads "Log In"
        await expect(login_button).to_have_text("Log In")

        # Locate username and password fields (adjust selectors as needed)
        username_field = page.locator("input[name='username']")
        password_field = page.locator("input[name='password']")
        # Ensure both fields are empty by default
        await expect(username_field).to_be_empty()
        await expect(password_field).to_be_empty()
        # Verify the login button is disabled when fields are empty
        await expect(login_button).to_be_disabled()

        await browser.close()

asyncio.run(run())