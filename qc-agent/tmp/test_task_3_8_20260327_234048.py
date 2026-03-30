import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto("https://example.com/login")

        # 1. Click "Forgot Password"
        await page.click('text="Forgot Password"')

        # 2. Verify password reset page loads
        await expect(page.locator('h1')).to_have_text("Reset Password")

        # 3. Enter registered email
        await page.fill('input[name="email"]', "user@example.com")

        # 4. Submit request
        await page.click('button[type="submit"]')

        # 5. Wait for confirmation toast
        await expect(page.locator('.toast')).to_have_text("Reset link sent")

        # 6. Simulate clicking the link in the email
        #    (In a real test, retrieve the token from the email service.)
        reset_link = "https://example.com/reset-password?token=abc123"
        await page.goto(reset_link)

        # 7. Verify password reset form loads
        await expect(page.locator('h1')).to_have_text("Set New Password")

        # 8. Enter new password and confirm
        await page.fill('input[name="new_password"]', "NewPass123!")
        await page.fill('input[name="confirm_password"]', "NewPass123!")

        # 9. Submit the new password
        await page.click('button[type="submit"]')

        # 10. Wait for success toast
        await expect(page.locator('.toast')).to_have_text("Password reset")

        # 11. Verify redirection back to the login page
        await expect(page).to_have_url("https://example.com/login")

        await browser.close()

asyncio.run(run())