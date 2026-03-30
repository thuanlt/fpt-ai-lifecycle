import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to login page
        await page.goto("https://example.com/login")
        # Wait for network idle to ensure page loads
        await page.wait_for_load_state("networkidle")
        # Verify page URL
        assert page.url == "https://example.com/login", f"Unexpected URL: {page.url}"
        # Locators for UI elements
        username = page.locator("#username")
        password = page.locator("#password")
        login_button = page.locator("button[type='submit']")
        forgot_password = page.locator("text=Forgot Password")
        signup_link = page.locator("text=Sign Up")
        # Verify all elements are visible
        await expect(username).to_be_visible()
        await expect(password).to_be_visible()
        await expect(login_button).to_be_visible()
        await expect(forgot_password).to_be_visible()
        await expect(signup_link).to_be_visible()
        # Close browser
        await context.close()
        await browser.close()

asyncio.run(main())