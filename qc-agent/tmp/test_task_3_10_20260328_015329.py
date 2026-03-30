import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Step 1: Log in as a regular user lacking the "Service Admin" role
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")
        await page.fill('input[name="username"]', "regular_user")
        await page.fill('input[name="password"]', "password123")
        await page.click('button[type="submit"]')
        # Wait until navigation/dashboard is loaded
        await page.wait_for_load_state("networkidle")
        # Simple verification that dashboard loaded (adjust selector as needed)
        assert await page.is_visible("text=Dashboard"), "Dashboard did not load after login"

        # ------------------------------------------------------------
        # Step 2: Navigate to the Service Catalog page
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-catalog")
        await page.wait_for_load_state("networkidle")

        # ------------------------------------------------------------
        # Step 3: Verify the "Create Service" button is hidden or disabled
        # ------------------------------------------------------------
        create_btn = page.locator('button:has-text("Create Service")')
        if await create_btn.is_visible():
            # Button is visible – ensure it is disabled
            disabled_attr = await create_btn.get_attribute("disabled")
            assert disabled_attr is not None, "Create Service button should be disabled for non‑admin users"
        else:
            # Button is not visible – acceptable outcome
            pass

        # ------------------------------------------------------------
        # Step 4: Attempt to directly access the creation URL
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-catalog/create")
        await page.wait_for_load_state("networkidle")
        # Verify that access is denied – either a redirect or an error message appears
        access_denied = await page.is_visible('text=Access Denied')
        permission_error = await page.is_visible('text=permission error')
        assert access_denied or permission_error, "User was able to access the create service page without proper permissions"

        # Clean up
        await browser.close()

asyncio.run(run())
