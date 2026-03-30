import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://example.com/login')
        # Verify heading font family
        heading = await page.locator('h1.login-heading')
        font_family = await heading.evaluate('(el) => window.getComputedStyle(el).fontFamily')
        assert font_family == 'Inter, sans-serif', f'Unexpected font family: {font_family}'
        # Verify label font size
        label = await page.locator('label[for\"username\"]')
        font_size = await label.evaluate('(el) => window.getComputedStyle(el).fontSize')
        assert font_size == '16px', f'Unexpected font size: {font_size}'
        await browser.close()

asyncio.run(run())