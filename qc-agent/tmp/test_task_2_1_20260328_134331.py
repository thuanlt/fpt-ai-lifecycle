import asyncio
from playwright.async_api import async_playwright, expect

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # List to capture any authentication requests
        auth_requests = []
        def on_request(request):
            # Adjust the endpoint pattern according to the actual application
            if "/auth" in request.url.lower() or "/login" in request.url.lower():
                auth_requests.append(request)
        page.on("request", on_request)

        # Navigate to the login page (replace with the real URL)
        await page.goto("https://example.com/login")

        # Click the Login button while leaving Username and Password empty
        await page.click("#loginButton")

        # Validate error messages are displayed
        username_error = page.locator("text=Username is required")
        password_error = page.locator("text=Password is required")
        await expect(username_error).to_be_visible()
        await expect(password_error).to_be_visible()

        # Verify that no authentication request was sent to the server
        assert len(auth_requests) == 0, f"Authentication request was sent: {[r.url for r in auth_requests]}"

        await browser.close()

asyncio.run(run_test())
