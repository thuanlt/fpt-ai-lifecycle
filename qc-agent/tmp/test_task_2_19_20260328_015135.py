import asyncio
from playwright.async_api import async_playwright


async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Navigate to the Service Catalog Management page.
        # Replace the URL with the actual environment under test.
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-catalog")
        await page.wait_for_selector("#tags-input")

        # -----------------------------------------------------------------
        # Test 1: Enter more than 10 comma‑separated tags and verify validation.
        # -----------------------------------------------------------------
        tags_exceed = ",".join([f"tag{i}" for i in range(11)])  # 11 tags → exceeds limit
        await page.fill("#tags-input", tags_exceed)
        await page.click("#save-button")

        # Expect the specific validation message about the maximum number of tags.
        max_tags_error = page.locator(".validation-error", has_text="Maximum of 10 tags allowed")
        await max_tags_error.wait_for(state="visible", timeout=5000)
        assert await max_tags_error.is_visible(), "Maximum tags validation error was not displayed"

        # Ensure that the save operation was blocked (no success toast appears).
        # Adjust the selector/value according to the actual implementation.
        success_toast = page.locator(".toast-success")
        assert not await success_toast.is_visible(), "Save succeeded despite validation error"

        # -----------------------------------------------------------------
        # Test 2: Include special characters in a tag and verify validation.
        # -----------------------------------------------------------------
        await page.fill("#tags-input", "validTag1,invalid!@#")
        await page.click("#save-button")

        char_error = page.locator(".validation-error", has_text="Tags may only contain alphanumeric characters")
        await char_error.wait_for(state="visible", timeout=5000)
        assert await char_error.is_visible(), "Alphanumeric characters validation error was not displayed"

        # Again, confirm that the save operation is prevented.
        assert not await success_toast.is_visible(), "Save succeeded despite invalid characters"

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
