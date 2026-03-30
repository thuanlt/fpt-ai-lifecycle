import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Login (adjust URL and selectors to your application)
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")
        await page.fill('input[name="username"]', "admin")
        await page.fill('input[name="password"]', "adminpass")
        await page.click('button[type="submit"]')

        # ------------------------------------------------------------
        # 2. Navigate to the Create User form
        # ------------------------------------------------------------
        await page.goto("https://example.com/admin/users/create")

        # ------------------------------------------------------------
        # 3. Fill out the Create User form
        # ------------------------------------------------------------
        await page.fill('input[name="fullName"]', "Test User")
        await page.fill('input[name="email"]', "test.user@example.com")
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "Password123!")
        # Select role "Administrator"
        await page.select_option('select[name="role"]', label="Administrator")
        # Submit the form
        await page.click('button:has-text("Save")')

        # ------------------------------------------------------------
        # 4. Verify the user appears in the list with the correct role
        # ------------------------------------------------------------
        await page.wait_for_selector('table#userTable')
        user_row = page.locator('table#userTable >> text="testuser"')
        await expect(user_row).to_be_visible()
        # Assuming the role is displayed in a <td> with a data attribute or known column index
        role_cell = user_row.locator('xpath=../..').locator('td[data-col="role"]')
        await expect(role_cell).to_have_text("Administrator")

        # ------------------------------------------------------------
        # 5. Open the edit dialog for the created user and verify role persists
        # ------------------------------------------------------------
        edit_button = user_row.locator('button:has-text("Edit")')
        await edit_button.click()
        role_select = page.locator('select[name="role"]')
        # Retrieve the selected option's visible text
        selected_label = await role_select.evaluate("""el => el.options[el.selectedIndex].text""")
        assert selected_label == "Administrator", f"Expected role Administrator, got {selected_label}"

        # ------------------------------------------------------------
        # 6. (Optional) Clean‑up – delete the test user
        # ------------------------------------------------------------
        await page.click('button:has-text("Delete")')
        await page.click('button:has-text("Confirm")')

        await browser.close()

asyncio.run(run())