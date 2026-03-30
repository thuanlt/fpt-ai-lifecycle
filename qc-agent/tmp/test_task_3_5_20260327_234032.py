import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to login page
        await page.goto("https://example.com/login")
        await page.wait_for_load_state("networkidle")

        # Enter valid username and incorrect password
        await page.fill('input[name="username"]', 'valid_user')
        await page.fill('input[name="password"]', 'wrong_password')

        # Click login button
        await page.click('button[type="submit"]')

        # Verify error toast appears
        toast_selector = '.toast'
        await page.wait_for_selector(toast_selector, timeout=5000)
        toast_text = await page.inner_text(toast_selector)
        assert "Invalid credentials" in toast_text, f"Expected toast to contain 'Invalid credentials', got '{toast_text}'"

        # Verify remains on login page
        current_url = page.url
        assert current_url.endswith("/login"), f"Expected to remain on login page, but navigated to {current_url}"

        print("Test passed: Failed login with wrong credentials shows error toast and stays on login page.")

        await context.close()
        await browser.close()

asyncio.run(run_test())