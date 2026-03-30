import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------------
        # STEP 1: Navigate to the application home page (replace with actual URL)
        # ---------------------------------------------------------------------
        await page.goto("http://localhost:3000")  # TODO: update to real base URL

        # ---------------------------------------------------------------
        # STEP 2: Open the Create User form via the Admin navigation menu
        # ---------------------------------------------------------------
        await page.click("text=Admin")
        await page.click("text=User Management")
        await page.click("text=Create User")

        # -------------------------------------------------
        # STEP 3: Verify the form and its UI components exist
        # -------------------------------------------------
        await page.wait_for_selector("form")
        username_input = await page.query_selector('input[name="username"]')
        email_input = await page.query_selector('input[name="email"]')
        password_input = await page.query_selector('input[name="password"]')
        role_select = await page.query_selector('select[name="role"]')
        save_button = await page.query_selector('button:has-text("Save")')

        assert username_input is not None, "Username field not found"
        assert email_input is not None, "Email field not found"
        assert password_input is not None, "Password field not found"
        assert role_select is not None, "Role dropdown not found"
        assert save_button is not None, "Save button not found"

        # ------------------------------------------------------------
        # STEP 4: Verify all input fields are empty and Save is disabled
        # ------------------------------------------------------------
        assert await username_input.input_value() == "", "Username field should be empty"
        assert await email_input.input_value() == "", "Email field should be empty"
        assert await password_input.input_value() == "", "Password field should be empty"
        # Role dropdown – assume the default value is empty or a placeholder like "Select..."
        selected_role = await role_select.evaluate("(el) => el.value")
        assert selected_role == "" or selected_role is None, "Role dropdown should have no selection"
        # Save button must be disabled
        is_disabled = await save_button.is_disabled()
        assert is_disabled, "Save button should be disabled when form is empty"

        # Clean up
        await browser.close()

asyncio.run(run())