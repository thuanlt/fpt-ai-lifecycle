import asyncio
from playwright.async_api import async_playwright

async def test_login_page_render():
    async with async_playwright() as p:
        # Launch Firefox in headless mode
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console messages
        console_messages = []

        async def on_console(msg):
            console_messages.append(msg)

        page.on("console", on_console)

        # Navigate to the login page
        await page.goto("https://example.com/login")

        # Wait for the main login form to be visible
        await page.wait_for_selector("#login-form", timeout=5000)

        # Verify the page title contains 'Login'
        title = await page.title()
        assert "Login" in title, f"Page title does not contain 'Login': {title}"

        # Verify there are no console errors
        error_msgs = [msg.text for msg in console_messages if msg.type == "error"]
        assert not error_msgs, f"Console errors found: {error_msgs}"

        await browser.close()

asyncio.run(test_login_page_render())