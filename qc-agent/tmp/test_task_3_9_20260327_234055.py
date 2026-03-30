import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to login page
        await page.goto('https://example.com/login')
        await expect(page).to_have_url('https://example.com/login')

        # 2. Enter valid credentials
        await page.fill('#username', 'valid_user')
        await page.fill('#password', 'ValidPass123!')
        await page.click('#loginButton')

        # Wait for MFA prompt
        await expect(page.locator('#mfaCode')).to_be_visible(timeout=5000)

        # 3. Enter correct MFA code
        await page.fill('#mfaCode', '123456')  # placeholder
        await page.click('#submitMFA')

        # Wait for navigation to dashboard
        await expect(page).to_have_url('https://example.com/dashboard', timeout=5000)

        # Verify welcome toast
        toast = page.locator('.toast')
        await expect(toast).to_be_visible(timeout=5000)
        await expect(toast).to_have_text('Welcome', timeout=5000)

        # Verify session cookie
        cookies = await context.cookies()
        session_cookie = next((c for c in cookies if c['name'] == 'session_id'), None)
        assert session_cookie is not None, 'Session cookie not found'

        print('Test passed: Successful login with MFA')

        await browser.close()

asyncio.run(run())