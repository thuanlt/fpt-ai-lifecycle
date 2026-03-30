import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to login page
        await page.goto('https://example.com/login')
        await expect(page).to_have_url('https://example.com/login')

        # 2. Enter valid username and password
        await page.fill('input[name\\"username\\"]', 'valid_user')
        await page.fill('input[name\\"password\\"]', 'ValidPass123!')
        # 3. Click login button
        await page.click('button[type\\"submit\\"]')

        # Wait for navigation to dashboard
        await page.wait_for_url('https://example.com/dashboard')
        assert page.url == 'https://example.com/dashboard'

        # Verify welcome toast appears
        toast_selector = '.toast-success'
        await expect(page.locator(toast_selector)).to_be_visible()
        toast_text = await page.locator(toast_selector).inner_text()
        assert 'Welcome' in toast_text

        print('Test passed: Successful login')

        await context.close()
        await browser.close()

asyncio.run(run())