import asyncio
from playwright.async_api import async_playwright, expect

async def test_update_quantity():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the application (replace with the real URL)
        # ------------------------------------------------------------
        await page.goto("https://example.com")

        # ------------------------------------------------------------
        # 2. Open the shopping cart
        # ------------------------------------------------------------
        # Adjust the selector to match the cart button in your app
        await page.click("button#cart")

        # ------------------------------------------------------------
        # 3. Locate the item controls inside the cart
        # ------------------------------------------------------------
        # These data-test attributes are placeholders – replace them with
        # the actual selectors used by the application.
        plus_button = page.locator("button[data-test='item-plus']")
        quantity_input = page.locator("input[data-test='item-quantity']")
        line_subtotal = page.locator("span[data-test='line-subtotal']")
        cart_total = page.locator("span[data-test='cart-total']")

        # ------------------------------------------------------------
        # 4. Verify the initial quantity is 1 (pre‑condition)
        # ------------------------------------------------------------
        await expect(quantity_input).to_have_value("1")

        # ------------------------------------------------------------
        # 5. Increase quantity from 1 to 3 using the plus button
        # ------------------------------------------------------------
        await plus_button.click()  # 1 -> 2
        await plus_button.click()  # 2 -> 3

        # ------------------------------------------------------------
        # 6. Assertions
        # ------------------------------------------------------------
        # a) Quantity field updates to "3"
        await expect(quantity_input).to_have_value("3")

        # b) Sub‑total for that line updates accordingly
        #    (Here we simply ensure the displayed text changes and is a
        #    numeric value greater than zero.)
        subtotal_text = await line_subtotal.text_content()
        assert subtotal_text is not None, "Line subtotal text should be present"
        # Extract numeric value (remove currency symbols, commas, etc.)
        subtotal_value = float(''.join(ch for ch in subtotal_text if ch.isdigit() or ch == '.'))
        assert subtotal_value > 0, "Line subtotal should be greater than 0"

        # c) Cart total reflects the new subtotal
        cart_total_text = await cart_total.text_content()
        assert cart_total_text is not None, "Cart total text should be present"
        cart_total_value = float(''.join(ch for ch in cart_total_text if ch.isdigit() or ch == '.'))
        # Assuming only one item in the cart for this test; otherwise, you would
        # calculate the expected total based on all line subtotals.
        assert abs(cart_total_value - subtotal_value) < 0.01, "Cart total should match the line subtotal"

        # ------------------------------------------------------------
        # 7. Clean up
        # ------------------------------------------------------------
        await context.close()
        await browser.close()

# Entry point for running the script directly
if __name__ == "__main__":
    asyncio.run(test_update_quantity())
