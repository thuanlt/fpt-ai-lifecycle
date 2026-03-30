import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the User Management page (replace with actual URL)
        await page.goto("http://your-app-url.com/admin/users")

        # --- Fill Create User Form ---
        await page.fill('input[name="username"]', 'testuser')
        await page.fill('input[name="email"]', 'test@example.com')
        await page.fill('input[name="password"]', 'Passw0rd!')
        # Select role "Editor" (adjust selector as needed)
        await page.select_option('select[name="role"]', label='Editor')
        # Click the Save button
        await page.click('button:has-text("Save")')

        # --- Assertions ---
        # Verify toast notification appears with correct text
        toast = page.locator('.toast-message')
        await expect(toast).to_have_text('User created successfully')

        # Verify the newly created user appears in the users table
        user_row = page.locator('table >> text=testuser')
        await expect(user_row).to_be_visible()
        # Optionally verify other columns (email, role)
        await expect(user_row.locator('td')).to_have_text([
            'testuser',
            'test@example.com',
            'Editor'
        ])

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run())
