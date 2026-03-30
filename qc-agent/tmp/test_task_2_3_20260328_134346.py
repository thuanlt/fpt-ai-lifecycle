import asyncio
from playwright.async_api import async_playwright, Page, Request

# Adjust these constants to match the actual application under test
LOGIN_URL = "https://example.com/login"
USERNAME_SELECTOR = "input[name=\"username\"]"
PASSWORD_SELECTOR = "input[name=\"password\"]"
LOGIN_BUTTON_SELECTOR = "button[type=\"submit\"]"
ERROR_MESSAGE_TEXT = "Password is required"
# The endpoint that handles login requests – update if different
LOGIN_ENDPOINT_SUBSTRING = "/login"

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for CI
        context = await browser.new_context()
        page = await context.new_page()

        # Flag to detect whether a login request was sent
        login_request_sent = False

        async def on_request(request: Request):
            nonlocal login_request_sent
            if LOGIN_ENDPOINT_SUBSTRING in request.url and request.method == "POST":
                login_request_sent = True
        page.on("request", on_request)

        # 1. Navigate to the login page
        await page.goto(LOGIN_URL)

        # 2. Enter a valid username (example value) and leave password blank
        await page.fill(USERNAME_SELECTOR, "valid_user@example.com")
        await page.fill(PASSWORD_SELECTOR, "")

        # 3. Click the Login button
        await page.click(LOGIN_BUTTON_SELECTOR)

        # 4. Verify the error message is displayed next to the password field
        #    We wait for the text to appear anywhere on the page; adjust selector if needed.
        try:
            await page.wait_for_selector(f"text={ERROR_MESSAGE_TEXT}", timeout=5000)
            print("✅ Error message displayed: \"Password is required\"")
        except Exception:
            print("❌ Expected error message not found.")
            await browser.close()
            return

        # 5. Verify that no login request was sent to the backend
        if login_request_sent:
            print("❌ Unexpected login request was sent to the backend.")
        else:
            print("✅ No login request was sent to the backend as expected.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
