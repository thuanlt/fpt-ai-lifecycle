import asyncio
from playwright.async_api import async_playwright

async def test_missing_shipping_address():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # Navigate to the Shipping step of the checkout flow.
        # Replace the URL with the actual environment under test.
        # ------------------------------------------------------------
        await page.goto("https://example.com/checkout/shipping")

        # Ensure all required address fields are empty.
        # Adjust selectors to match the real application.
        await page.fill('input[name="street"]', "")
        await page.fill('input[name="city"]', "")
        await page.fill('input[name="zip"]', "")
        await page.fill('input[name="state"]', "")
        await page.fill('input[name="country"]', "")

        # Attempt to proceed to the next step.
        await page.click('button:has-text("Continue to Payment")')

        # -----------------------------------------------------------------
        # Expected Result 1: Inline validation errors appear for each required field.
        # -----------------------------------------------------------------
        street_error = await page.text_content('text=Street address is required')
        assert street_error is not None, "Street address error not displayed"
        city_error = await page.text_content('text=City is required')
        assert city_error is not None, "City error not displayed"
        zip_error = await page.text_content('text=ZIP code is required')
        assert zip_error is not None, "ZIP code error not displayed"
        # Add more assertions if other fields have specific messages.

        # ---------------------------------------------------------------
        # Expected Result 2: "Continue to Payment" button remains disabled.
        # ---------------------------------------------------------------
        continue_btn = await page.query_selector('button:has-text("Continue to Payment")')
        disabled_attr = await continue_btn.get_attribute('disabled')
        assert disabled_attr is not None, "Continue button should be disabled when required fields are empty"

        await browser.close()

asyncio.run(test_missing_shipping_address())
