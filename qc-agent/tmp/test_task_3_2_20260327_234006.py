import asyncio
from playwright.async_api import async_playwright

async def test_verify_password_field():
    """Verify that the password field is present and visible on the login page."""
    async with async_playwright() as p:
        # Launch the browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto("https://example.com/login")

        # Wait for the password input to be visible
        await page.wait_for_selector("input[type='password']", state="visible")

        # Optionally, assert that the element is indeed visible
        password_input = await page.query_selector("input[type='password']")
        assert password_input is not None, "Password field not found"
        is_visible = await password_input.is_visible()
        assert is_visible, "Password field is not visible"

        print("✅ Password field is present and visible.")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_verify_password_field())
