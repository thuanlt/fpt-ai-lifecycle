import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch Chromium (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=False)
        # Set viewport to mobile size 375x667
        context = await browser.new_context(viewport={"width": 375, "height": 667})
        page = await context.new_page()
        # Navigate to the login page – replace with the actual URL if different
        await page.goto("http://localhost/login")

        # Define locators (adjust selectors to match the actual page)
        username = page.locator("#username")
        password = page.locator("#password")
        login_btn = page.locator("#loginButton")

        # Ensure elements are present
        await username.wait_for(state="visible")
        await password.wait_for(state="visible")
        await login_btn.wait_for(state="visible")

        # Capture bounding boxes for layout verification
        username_box = await username.bounding_box()
        password_box = await password.bounding_box()
        login_box = await login_btn.bounding_box()

        # ---- Verification Steps ----
        # 1. Username and password fields should be stacked vertically
        #    • X‑coordinates should be almost identical
        #    • Password field Y should be greater than Username field Y
        assert abs(username_box["x"] - password_box["x"]) < 5, "Username and password fields are not aligned vertically"
        assert password_box["y"] > username_box["y"], "Password field is not positioned below the username field"

        # 2. Login button should span the full width (allowing for reasonable margins)
        #    • Width should be close to the viewport width (e.g., >= 350px for a 375px viewport)
        #    • Left and right margins should be roughly equal
        assert login_box["width"] >= 350, "Login button does not span the expected width"
        left_margin = login_box["x"]
        right_margin = 375 - (login_box["x"] + login_box["width"])
        assert abs(left_margin - right_margin) < 20, "Login button margins are not balanced"

        print("Responsive design verification passed.")

        await browser.close()

asyncio.run(run())