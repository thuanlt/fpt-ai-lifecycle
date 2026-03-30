import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch Safari (WebKit) browser
        browser = await p.webkit.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)

        # Navigate to the login page
        await page.goto("https://example.com/login")

        # Wait for the login form to be visible
        await page.wait_for_selector("#login-form", state="visible", timeout=5000)

        # Verify no console errors were logged
        assert len(console_errors) == 0, f"Console errors found: {[msg.text for msg in console_errors]}"

        print("Test passed: Page rendered correctly and no console errors.")

        await browser.close()

asyncio.run(run())