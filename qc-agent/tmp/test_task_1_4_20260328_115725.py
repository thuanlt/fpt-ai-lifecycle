import asyncio
from playwright.async_api import async_playwright, expect

async def test_description_max_length():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to Service Management page
        await page.goto("https://example.com/service-management")
        # Open the Create Service modal
        await page.click("button#create-service")
        # Input a description longer than 500 characters
        long_text = "a" * 501
        await page.fill("textarea#service-description", long_text)
        # Click Save button
        await page.click("button#save-service")
        # Verify validation error message
        error = page.locator("text=Description cannot exceed 500 characters")
        await expect(error).to_be_visible()
        # Verify the modal remains open
        modal = page.locator("#service-modal")
        await expect(modal).to_be_visible()
        await browser.close()

asyncio.run(test_description_max_length())