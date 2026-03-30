import asyncio
from playwright.async_api import async_playwright

async def test_username_field_visible():
    """Verify that the username field is visible on the login page."""
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Replace with the actual login page URL
        login_url = "https://example.com/login"
        await page.goto(login_url)

        # Selector for the username input field (adjust as needed)
        username_selector = "input[name='username']"

        # Wait for the element to be attached to the DOM
        await page.wait_for_selector(username_selector, state="attached")

        # Assert that the element is visible
        is_visible = await page.is_visible(username_selector)
        assert is_visible, f"Username field '{username_selector}' is not visible on {login_url}"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_username_field_visible())
