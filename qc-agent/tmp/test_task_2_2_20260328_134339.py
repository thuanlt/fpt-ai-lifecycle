import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Intercept login request to verify it is not sent
        login_requested = False
        async def handle_route(route, request):
            nonlocal login_requested
            if "/api/login" in request.url:
                login_requested = True
            await route.continue_()
        await context.route("**/*", handle_route)
        # Navigate to login page
        await page.goto("https://example.com/login")
        # Fill password, leave username empty
        await page.fill('input[name="password"]', 'ValidPassword123')
        # Click login button
        await page.click('button[type="submit"]')
        # Assert error message for username
        error_locator = page.locator('text=Username is required')
        await error_locator.wait_for(state='visible', timeout=5000)
        assert await error_locator.is_visible(), "Username required error not displayed"
        # Verify no login request was made
        assert not login_requested, "Login request was transmitted despite empty username"
        await browser.close()

asyncio.run(run_test())