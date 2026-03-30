import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page (replace with actual URL)
        await page.goto("http://example.com/login")

        # Selectors – adjust according to the actual application
        username_input = "input[name='username']"
        password_input = "input[name='password']"
        submit_button = "button[type='submit']"
        username_error_msg = "text=Username is required"
        password_error_msg = "text=Password is required"

        # Ensure fields are empty (they are by default, but clear just in case)
        await page.fill(username_input, "")
        await page.fill(password_input, "")

        # Click the Submit button
        await page.click(submit_button)

        # Verify inline validation messages are displayed
        await expect(page.locator(username_error_msg)).to_be_visible()
        await expect(page.locator(password_error_msg)).to_be_visible()

        await browser.close()

asyncio.run(run())