import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        user_data_dir = "./tmp_user_data"
        # Launch persistent context
        context = await p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = await context.new_page()
        await page.goto("https://example.com/login")
        # Fill credentials
        await page.fill("#username", "testuser")
        await page.fill("#password", "Password123!")
        # Click remember me
        await page.check("#rememberMe")
        # Click login
        await page.click("#loginButton")
        # Wait for navigation or success indicator
        await page.wait_for_selector("#dashboard", timeout=5000)
        # Verify no validation error
        errors = await page.locator(".error").all()
        assert len(errors) == 0, "Validation errors found after login"
        # Close context
        await context.close()
        # Reopen new context with same user data dir
        context2 = await p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page2 = await context2.new_page()
        await page2.goto("https://example.com")
        # Verify user remains logged in
        assert await page2.locator("#logoutButton").is_visible(), "User not logged in after reopening browser"
        await context2.close()

asyncio.run(run())