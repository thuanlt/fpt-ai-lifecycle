import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto("https://example.com/login")
        await expect(page).to_have_url("https://example.com/login")

        # Enter locked username and any password
        await page.fill("#username", "locked_user")
        await page.fill("#password", "anyPassword123")

        # Click the login button
        await page.click("#loginButton")

        # Verify the error toast appears with the correct message
        toast_selector = ".toast"
        await expect(page.locator(toast_selector)).to_be_visible()
        toast_text = await page.locator(toast_selector).inner_text()
        assert toast_text.strip() == "Account locked", f"Unexpected toast: {toast_text}"

        # Verify the user remains on the login page
        assert page.url == "https://example.com/login", f"Unexpected navigation to {page.url}"

        print("Test passed.")
        await context.close()
        await browser.close()

asyncio.run(run())