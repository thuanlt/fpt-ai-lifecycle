import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the login page (replace with actual URL)
        await page.goto("https://example.com/login")

        # Step 1: Enter a valid username
        await page.fill('input[name="username"]', 'validUser')

        # Step 2: Enter a 128‑character password (exceeds allowed length)
        long_password = 'a' * 128
        await page.fill('input[name="password"]', long_password)

        # Step 3: Click the Submit button
        await page.click('button[type="submit"]')

        # Expected Result: Inline validation message appears
        await page.wait_for_selector('text=Password exceeds maximum length', timeout=5000)
        print("✅ Validation message displayed as expected.")

        await browser.close()

asyncio.run(run_test())
