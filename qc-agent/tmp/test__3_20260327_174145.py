import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the chat application
        await page.goto("https://your-app-url.example.com")

        # Step 1: Click the "Không" button
        await page.locator("text=Không").click()

        # Expected Result 1: Closing message is displayed
        closing_message = page.locator("text=Cảm ơn bạn. Nếu cần hỗ trợ thêm, vui lòng liên hệ lại.")
        await expect(closing_message).to_be_visible()

        # Expected Result 2: No further input fields are shown (e.g., input or textarea)
        input_fields = page.locator("input, textarea")
        await expect(input_fields).to_have_count(0)

        await browser.close()

asyncio.run(run())
