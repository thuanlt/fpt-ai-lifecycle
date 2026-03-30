import asyncio
from playwright.async_api import async_playwright, expect

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page – replace with actual URL
        await page.goto("https://example.com/login")

        # Click the "Sign In" button without filling any fields
        await page.get_by_role("button", name="Sign In").click()

        # Verify the inline validation messages appear
        email_error = page.get_by_text("Email is required", exact=True)
        password_error = page.get_by_text("Password is required", exact=True)

        await expect(email_error).to_be_visible()
        await expect(password_error).to_be_visible()

        # Close browser
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
