import asyncio
from playwright.async_api import async_playwright, expect

async def test_registration_required_fields():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the registration page
        await page.goto("https://example.com/register")

        # Click the Submit button without entering any data
        await page.click('button:has-text("Submit")')

        # Verify that the required‑field error messages are displayed
        first_name_error = page.locator('text=First Name is required')
        await expect(first_name_error).to_be_visible()

        last_name_error = page.locator('text=Last Name is required')
        await expect(last_name_error).to_be_visible()

        email_error = page.locator('text=Email is required')
        await expect(email_error).to_be_visible()

        # Verify that the user remains on the registration page
        await expect(page).to_have_url("**/register**")

        await context.close()
        await browser.close()

asyncio.run(test_registration_required_fields())
