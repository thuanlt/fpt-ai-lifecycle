import asyncio
from playwright.async_api import async_playwright

# Replace with your actual login page URL
BASE_URL = "https://example.com/login"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (Chromium used here; adjust if needed)
        browser = await p.chromium.launch(headless=True)
        # Create a new context with tablet viewport size
        context = await browser.new_context(viewport={"width": 768, "height": 1024})
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(BASE_URL)
        await page.wait_for_load_state("networkidle")

        # Locate the login form (adjust selector to match your markup)
        login_form = page.locator("form#loginForm")
        await login_form.wait_for(state="visible")

        # Get viewport dimensions
        viewport_width = await page.evaluate("() => window.innerWidth")
        viewport_height = await page.evaluate("() => window.innerHeight")

        # Get form bounding box
        box = await login_form.bounding_box()
        if not box:
            raise AssertionError("Login form not found on the page.")

        form_left = box["x"]
        form_top = box["y"]
        form_width = box["width"]
        form_height = box["height"]

        # 1. Verify that the form width is less than or equal to the viewport width
        assert form_width <= viewport_width, (
            f"Form width ({form_width}px) exceeds viewport width ({viewport_width}px)."
        )

        # 2. Verify that the form is horizontally centered (allow small tolerance)
        horizontal_margin = abs((viewport_width - form_width) / 2 - form_left)
        assert horizontal_margin < 5, (
            f"Form is not centered horizontally. Margin difference: {horizontal_margin}px."
        )

        # 3. Verify that the form is vertically positioned within the viewport (optional)
        vertical_margin = abs((viewport_height - form_height) / 2 - form_top)
        assert vertical_margin < 20, (
            f"Form is not vertically centered. Margin difference: {vertical_margin}px."
        )

        print("✅ Tablet layout and centering verified successfully.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
