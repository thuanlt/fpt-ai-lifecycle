import asyncio
from playwright.async_api import async_playwright, expect

# Expected brand colors (replace with actual hex values)
EXPECTED_BUTTON_COLOR = "rgb(0, 123, 255)"  # Example: primary brand blue
EXPECTED_BACKGROUND_COLOR = "rgb(255, 255, 255)"  # Example: white background

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Wait for the login button to be visible
        login_button_selector = "#login-button"  # Replace with actual selector
        await page.wait_for_selector(login_button_selector)

        # Retrieve the computed color of the login button
        button_color = await page.eval_on_selector(
            login_button_selector,
            "el => getComputedStyle(el).backgroundColor"
        )
        print(f"Login button color: {button_color}")
        assert button_color == EXPECTED_BUTTON_COLOR, (
            f"Expected button color {EXPECTED_BUTTON_COLOR}, got {button_color}"
        )

        # Retrieve the computed background color of the page body
        body_color = await page.eval_on_selector(
            "body",
            "el => getComputedStyle(el).backgroundColor"
        )
        print(f"Background color: {body_color}")
        assert body_color == EXPECTED_BACKGROUND_COLOR, (
            f"Expected background color {EXPECTED_BACKGROUND_COLOR}, got {body_color}"
        )

        # Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
