import asyncio
from playwright.async_api import async_playwright, expect

# Replace this URL with the actual login page URL of the application under test
LOGIN_URL = "https://example.com/login"

# Selectors – update these to match the real application's DOM
USERNAME_SELECTOR = "input[name='username']"  # or email field
PASSWORD_SELECTOR = "input[name='password']"
LOGIN_BUTTON_SELECTOR = "button[type='submit']"
USERNAME_ERROR_SELECTOR = "#username-error"   # element that shows "Username or Email is required"
PASSWORD_ERROR_SELECTOR = "#password-error"   # element that shows "Password is required"

async def test_required_field_validation():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(LOGIN_URL)

        # Ensure the fields are empty (they should be by default, but clear just in case)
        await page.fill(USERNAME_SELECTOR, "")
        await page.fill(PASSWORD_SELECTOR, "")

        # Click the Login button
        await page.click(LOGIN_BUTTON_SELECTOR)

        # Assertions – verify inline error messages appear
        username_error = page.locator(USERNAME_ERROR_SELECTOR)
        password_error = page.locator(PASSWORD_ERROR_SELECTOR)

        await expect(username_error).to_be_visible()
        await expect(username_error).to_have_text("Username or Email is required")

        await expect(password_error).to_be_visible()
        await expect(password_error).to_have_text("Password is required")

        # Verify that no network request to the login endpoint was made
        # This assumes the login request is a POST to /api/login – adjust as needed
        login_requests = []
        async def handle_route(route, request):
            if "/api/login" in request.url and request.method == "POST":
                login_requests.append(request)
            await route.continue_()

        await context.route("**/*", handle_route)
        # Re‑trigger the click to capture any potential request after the handler is attached
        await page.click(LOGIN_BUTTON_SELECTOR)
        assert len(login_requests) == 0, "Login request was sent despite validation errors"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_required_field_validation())
