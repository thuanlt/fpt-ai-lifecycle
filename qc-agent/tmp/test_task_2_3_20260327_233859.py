import asyncio
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Test: Username contains invalid characters
# ---------------------------------------------------------------------------
# Expected behaviour:
#   - Inline error message: "Username contains invalid characters." (C06)
#   - No toast error should appear.
# ---------------------------------------------------------------------------

async def test_username_special_characters():
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page – replace with the actual URL
        await page.goto("https://example.com/login")

        # -------------------------------------------------------------------
        # Locate elements – update selectors to match the real application
        # -------------------------------------------------------------------
        username_selector = "#username"          # CSS selector for username field
        password_selector = "#password"          # CSS selector for password field
        login_button_selector = "#loginButton"   # CSS selector for login button
        inline_error_selector = ".error-message"  # CSS selector for inline error
        toast_error_selector = ".toast-error"     # CSS selector for toast error

        # -------------------------------------------------------------------
        # Step 1: Enter invalid username and a valid password
        # -------------------------------------------------------------------
        await page.fill(username_selector, "invalid!@#$%")
        await page.fill(password_selector, "ValidPass123")

        # -------------------------------------------------------------------
        # Step 2: Click the login button
        # -------------------------------------------------------------------
        await page.click(login_button_selector)

        # -------------------------------------------------------------------
        # Step 3: Verify inline error message
        # -------------------------------------------------------------------
        try:
            await page.wait_for_selector(inline_error_selector, timeout=5000)
            error_text = await page.text_content(inline_error_selector)
            assert error_text.strip() == "Username contains invalid characters.", f"Unexpected inline error: {error_text}"
            print("✅ Inline error message verified.")
        except Exception as e:
            print(f"❌ Inline error verification failed: {e}")
            raise

        # -------------------------------------------------------------------
        # Step 4: Verify that no toast error appears
        # -------------------------------------------------------------------
        toast_element = await page.query_selector(toast_error_selector)
        assert toast_element is None, "Toast error should not be displayed."
        print("✅ No toast error displayed.")

        # Clean up
        await context.close()
        await browser.close()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(test_username_special_characters())
