import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page – replace with actual URL
        await page.goto("http://example.com/login")

        # Prepare a username longer than the allowed 50 characters
        long_username = "a" * 51

        # Fill the login form
        await page.fill('input[name="username"]', long_username)
        await page.fill('input[name="password"]', "ValidPassword123")
        await page.click('button:has-text("Login")')

        # Verify the inline validation message is displayed
        validation_message = page.locator('text=Username cannot exceed 50 characters')
        await expect(validation_message).to_be_visible()

        # Optionally ensure that no network request for login is sent (client‑side block)
        # This can be done by asserting that the request payload does not contain the login endpoint.
        # For simplicity, we rely on the presence of the validation message.

        await browser.close()

asyncio.run(run())