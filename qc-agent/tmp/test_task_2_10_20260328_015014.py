import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match the actual application under test
URL = "http://example.com/service-catalog"  # <-- replace with real URL
PRICE_INPUT_SELECTOR = "input[name='price']"  # <-- replace with actual selector
SAVE_BUTTON_SELECTOR = "button:has-text('Save')"  # <-- replace with actual selector
ERROR_MESSAGE_SELECTOR = "div.error-message"  # <-- replace with actual selector that shows validation errors

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Service Catalog Management page
        await page.goto(URL)
        await page.wait_for_load_state("networkidle")

        # -----------------------------------------------------------------
        # Test Step 1: Verify that leaving the Price field blank shows a required error
        # -----------------------------------------------------------------
        # Ensure the price field is empty (clear any pre‑filled value)
        await page.fill(PRICE_INPUT_SELECTOR, "")
        # Click the Save button
        await page.click(SAVE_BUTTON_SELECTOR)
        # Assert that the required validation message appears
        required_error = await page.locator(ERROR_MESSAGE_SELECTOR, has_text="Price is required")
        await expect(required_error).to_be_visible(timeout=5000)
        # Optionally, ensure that the form was not submitted (URL unchanged)
        await expect(page).to_have_url(URL)

        # -----------------------------------------------------------------
        # Test Step 2: Verify that entering a non‑numeric value shows a format error
        # -----------------------------------------------------------------
        # Fill the Price field with a non‑numeric string
        await page.fill(PRICE_INPUT_SELECTOR, "Free")
        # Click the Save button again
        await page.click(SAVE_BUTTON_SELECTOR)
        # Assert that the numeric‑value validation message appears
        numeric_error = await page.locator(ERROR_MESSAGE_SELECTOR, has_text="Price must be a numeric value")
        await expect(numeric_error).to_be_visible(timeout=5000)
        # Ensure the form is still on the same page (save prevented)
        await expect(page).to_have_url(URL)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
