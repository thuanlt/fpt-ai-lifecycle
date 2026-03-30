import asyncio
from playwright.async_api import async_playwright, expect

# Replace with the actual URL of the login page
BASE_URL = "https://example.com/login"

async def run_test():
    async with async_playwright() as p:
        # Launch Chromium in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 375, "height": 667})
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(BASE_URL)

        # --- 1. Verify page adapts to mobile layout ---
        # Check that the main container has a mobile-specific class or style
        # (Assuming a class "mobile-layout" is added for mobile viewports)
        await expect(page.locator("body")).to_have_class(re.compile(r".*mobile-layout.*"))

        # --- 2. Verify elements stack vertically ---
        # Locate the username and password input fields and the login button
        username_input = page.locator("input[name='username']")
        password_input = page.locator("input[name='password']")
        login_button = page.locator("button[type='submit']")

        # Ensure all elements are visible
        await expect(username_input).to_be_visible()
        await expect(password_input).to_be_visible()
        await expect(login_button).to_be_visible()

        # Get bounding boxes to confirm vertical stacking
        username_box = await username_input.bounding_box()
        password_box = await password_input.bounding_box()
        button_box = await login_button.bounding_box()

        assert username_box is not None and password_box is not None and button_box is not None, "Bounding boxes could not be retrieved"

        # Username should be above password, which should be above button
        assert username_box["y"] < password_box["y"], "Username input is not above password input"
        assert password_box["y"] < button_box["y"], "Password input is not above login button"

        # --- 3. Verify input fields occupy full width ---
        viewport_width = 375
        # Allow a small margin for padding/border (e.g., 10px total)
        margin_tolerance = 10
        assert abs(username_box["width"] - viewport_width) <= margin_tolerance, "Username input does not span full width"
        assert abs(password_box["width"] - viewport_width) <= margin_tolerance, "Password input does not span full width"

        # --- 4. Verify login button width ---
        assert abs(button_box["width"] - viewport_width) <= margin_tolerance, "Login button does not span full width"

        print("All UI/UX assertions passed for mobile viewport.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
