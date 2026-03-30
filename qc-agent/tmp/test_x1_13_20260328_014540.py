import asyncio
from playwright.async_api import async_playwright


async def test_add_out_of_stock_product():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the application – replace with the real URL.
        # ------------------------------------------------------------
        await page.goto("https://your-app-url.com")

        # ------------------------------------------------------------
        # 2. Locate a product that is marked "Out of Stock".
        #    The selector below assumes the product card carries a
        #    data-test-id attribute; adjust according to the actual DOM.
        # ------------------------------------------------------------
        product_selector = "[data-test-id='product-out-of-stock']"
        await page.wait_for_selector(product_selector)

        # ------------------------------------------------------------
        # 3. Within that product card, find the "Add to Cart" button.
        # ------------------------------------------------------------
        add_to_cart_button_selector = f"{product_selector} button[data-test-id='add-to-cart']"
        button = await page.query_selector(add_to_cart_button_selector)
        assert button is not None, "Add to Cart button not found for out‑of‑stock product"

        # ------------------------------------------------------------
        # 4. Verify the button is either disabled or shows a tooltip
        #    containing the word "Unavailable".
        # ------------------------------------------------------------
        is_disabled = await button.get_attribute("disabled")
        tooltip = await button.get_attribute("title")
        assert (
            is_disabled is not None
            or (tooltip and "Unavailable" in tooltip)
        ), "Add to Cart button should be disabled or display an 'Unavailable' tooltip"

        # ------------------------------------------------------------
        # 5. Attempt to click the button – the click should have no effect.
        # ------------------------------------------------------------
        try:
            await button.click()
        except Exception:
            # Some browsers raise when clicking a disabled element; ignore.
            pass

        # ------------------------------------------------------------
        # 6. Verify that the product was NOT added to the cart.
        #    Navigate to the cart page (adjust URL/selector as needed).
        # ------------------------------------------------------------
        await page.goto("https://your-app-url.com/cart")
        # Look for any cart item that matches the out‑of‑stock product ID.
        out_of_stock_cart_item = await page.query_selector(
            "[data-test-id='cart-item'][data-product-id='out-of-stock']"
        )
        assert out_of_stock_cart_item is None, "Out‑of‑stock product was unexpectedly added to the cart"

        # ------------------------------------------------------------
        # 7. Verify that a notification with the expected text appears.
        # ------------------------------------------------------------
        notification = await page.wait_for_selector(
            "text=Product is out of stock", timeout=5000
        )
        assert notification is not None, "Expected 'Product is out of stock' notification did not appear"

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_add_out_of_stock_product())
