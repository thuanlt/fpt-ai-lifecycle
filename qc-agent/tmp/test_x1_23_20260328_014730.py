import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Log in (adjust selectors/URL to match the actual app)
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "Password123")
        await page.click('button:has-text("Login")')
        # Wait until navigation/network is idle after login
        await page.wait_for_load_state("networkidle")

        # ------------------------------------------------------------
        # 2. Navigate to the User Profile page
        # ------------------------------------------------------------
        await page.goto("https://example.com/profile")
        await page.wait_for_load_state("networkidle")

        # ------------------------------------------------------------
        # 3. Prepare to capture the PATCH request that updates the user
        # ------------------------------------------------------------
        async with page.expect_response(
            lambda resp: (
                "/api/users/" in resp.url and resp.request.method == "PATCH"
            )
        ) as patch_response:
            # --------------------------------------------------------
            # 4. Change first name to "Anna" and click Save
            # --------------------------------------------------------
            await page.fill('input[name="firstName"]', "Anna")
            await page.click('button:has-text("Save")')
        # ------------------------------------------------------------
        # 5. Validate the PATCH request succeeded
        # ------------------------------------------------------------
        response = await patch_response.value
        assert response.ok, f"PATCH request failed with status {response.status}"

        # ------------------------------------------------------------
        # 6. Verify success toast appears
        # ------------------------------------------------------------
        toast = await page.wait_for_selector('text=Profile updated successfully', timeout=5000)
        assert toast is not None, "Success toast 'Profile updated successfully' was not displayed"

        # ------------------------------------------------------------
        # 7. Verify the displayed name updates to "Anna"
        # ------------------------------------------------------------
        displayed_name = await page.inner_text('.profile-name')
        assert displayed_name == "Anna", f"Displayed name is '{displayed_name}' instead of 'Anna'"

        # Clean up
        await browser.close()

asyncio.run(run())
