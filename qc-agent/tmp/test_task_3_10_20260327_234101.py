import asyncio
from playwright.async_api import async_playwright, expect

async def test_mfa_wrong():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to login page
        await page.goto('https://example.com/login')
        await expect(page).to_have_url('https://example.com/login')

        # 2. Enter valid credentials
        await page.fill('#username', 'valid_user')
        await page.fill('#password', 'valid_password')
        await page.click('#loginBtn')
        await expect(page).to_have_url('https://example.com/mfa')

        # 3. Enter incorrect MFA code
        await page.fill('#mfaCode', '123456')
        await page.click('#submitMFA')

        # Verify error toast
        toast = page.locator('.toast')
        await expect(toast).to_be_visible()
        await expect(toast).to_have_text('Invalid MFA code')

        # Ensure we remain on MFA page
        await expect(page).to_have_url('https://example.com/mfa')

        await browser.close()

asyncio.run(test_mfa_wrong())