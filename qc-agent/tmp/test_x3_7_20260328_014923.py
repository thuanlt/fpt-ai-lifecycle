import asyncio
from playwright.async_api import async_playwright, expect

async def run_test():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the User Management page where the Create User form lives
        # ------------------------------------------------------------
        await page.goto("https://example.com/admin/users")  # TODO: replace with the real URL

        # ------------------------------------------------------------
        # 2. Fill the form with a duplicate username ("testuser")
        # ------------------------------------------------------------
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="email"]', "newuser@example.com")
        await page.fill('input[name="password"]', "Password123!")

        # ------------------------------------------------------------
        # 3. Submit the form
        # ------------------------------------------------------------
        await page.click('button:has-text("Save")')

        # ------------------------------------------------------------
        # 4. Verify that the error dialog is shown with the expected message
        # ------------------------------------------------------------
        error_dialog = page.locator('text=Username already exists')
        await expect(error_dialog).to_be_visible()

        # ------------------------------------------------------------
        # 5. Verify that no new user record has been added to the list
        #    (the list should still contain only the original "testuser")
        # ------------------------------------------------------------
        # Refresh the user list (optional – depends on app behaviour)
        await page.goto("https://example.com/admin/users")
        user_rows = page.locator(f'text={"testuser"}')
        # Expect exactly one occurrence – the pre‑existing user
        await expect(user_rows).to_have_count(1)

        # Clean up
        await context.close()
        await browser.close()

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(run_test())
