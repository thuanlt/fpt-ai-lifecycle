import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Flag to detect any login request being sent
        login_requested = False
        def request_handler(request):
            nonlocal login_requested
            # Adjust the endpoint fragment according to the actual application
            if request.method == "POST" and "/login" in request.url:
                login_requested = True
        page.on("request", request_handler)

        # Navigate to the login page – replace with the real URL
        await page.goto("http://example.com/login")

        # Fill in invalid email and any password
        await page.fill('input[name="username"]', 'invalidemail')
        await page.fill('input[name="password"]', 'anyPassword123')

        # Click the Sign In button
        await page.click('button:has-text("Sign In")')

        # Verify the inline validation error appears
        error_locator = await page.wait_for_selector(
            "text=Please enter a valid email address",
            timeout=5000
        )
        assert error_locator is not None, "Expected validation error message not displayed"

        # Give a short moment for any stray network calls
        await asyncio.sleep(1)
        assert not login_requested, "Login request was sent despite invalid email format"

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
