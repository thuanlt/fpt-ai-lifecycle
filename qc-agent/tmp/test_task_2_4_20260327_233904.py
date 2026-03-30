import asyncio
from playwright.async_api import async_playwright

# Replace with the actual URL of the login page
BASE_URL = "https://example.com/login"

async def test_login_invalid_email():
    async with async_playwright() as p:
        # Launch browser (headless=False for debugging, set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(BASE_URL)

        # Selectors – adjust these to match the actual application
        email_selector = "#email"          # Username / Email input field
        password_selector = "#password"    # Password input field
        login_button_selector = "#loginButton"  # Login button
        inline_error_selector = ".inline-error"  # Inline error message element
        toast_error_selector = ".toast"   # Toast notification element

        # 1. Enter an incorrectly formatted email and a dummy password
        await page.fill(email_selector, "user@@example.com")
        await page.fill(password_selector, "ValidPassword123!")

        # 2. Click the login button
        await page.click(login_button_selector)

        # 3. Verify the inline error message appears with the correct text
        await page.wait_for_selector(inline_error_selector, state="visible", timeout=5000)
        error_text = await page.text_content(inline_error_selector)
        assert error_text.strip() == "Invalid email format.", f"Unexpected inline error: {error_text}"

        # 4. Verify that no toast error is displayed
        # Wait briefly to allow any toast to appear, then confirm it is not visible
        try:
            await page.wait_for_selector(toast_error_selector, state="visible", timeout=2000)
            toast_visible = True
        except asyncio.TimeoutError:
            toast_visible = False
        assert not toast_visible, "Toast error should not be displayed for invalid email format."

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login_invalid_email())
