import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------------
        # Capture any network request that targets the login endpoint.
        # Adjust the substring "login" to match the actual endpoint used by the app.
        # ---------------------------------------------------------------------
        login_requests = []
        def on_request(request):
            if "login" in request.url.lower():
                login_requests.append(request)
        page.on("request", on_request)

        # Navigate to the login page – replace with the real URL.
        await page.goto("https://example.com/login")

        # ---------------------------------------------------------------------
        # Step 1: Fill in a valid username.
        # ---------------------------------------------------------------------
        await page.fill('input[name="username"]', "validUser")

        # ---------------------------------------------------------------------
        # Step 2: Enter a password that lacks numeric characters.
        # ---------------------------------------------------------------------
        await page.fill('input[name="password"]', "Password")  # No numbers

        # ---------------------------------------------------------------------
        # Step 3: Click the Login button.
        # Adjust the selector if the button uses a different identifier.
        # ---------------------------------------------------------------------
        await page.click('button:has-text("Login")')

        # ---------------------------------------------------------------------
        # Expected Result 1: Validation message is displayed.
        # ---------------------------------------------------------------------
        error_message = page.locator('text=Password must include at least one numeric character')
        await expect(error_message).to_be_visible(timeout=5000)

        # ---------------------------------------------------------------------
        # Expected Result 2: No login request is sent to the backend.
        # ---------------------------------------------------------------------
        login_sent = any("login" in req.url.lower() for req in login_requests)
        assert not login_sent, "Login request was sent despite validation failure"

        await browser.close()

asyncio.run(run())
