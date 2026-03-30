import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # STEP 1: Navigate to the application home page
        # ------------------------------------------------------------
        await page.goto("https://example.com")  # TODO: replace with actual URL

        # ------------------------------------------------------------
        # STEP 2: Add first product to the cart
        # ------------------------------------------------------------
        # Click on a product (replace selector with real one)
        await page.click("text=Product 1")
        # Click the "Add to Cart" button for the selected product
        await page.click("button:has-text('Add to Cart')")

        # ------------------------------------------------------------
        # STEP 3: Add second product to the cart
        # ------------------------------------------------------------
        await page.click("text=Product 2")
        await page.click("button:has-text('Add to Cart')")

        # ------------------------------------------------------------
        # STEP 4: Verify cart icon badge displays count "2"
        # ------------------------------------------------------------
        # Assuming the badge is a child element of the cart icon
        badge_selector = "#cart-icon .badge"
        await page.wait_for_selector(badge_selector)
        badge_text = await page.inner_text(badge_selector)
        assert badge_text == "2", f"Expected cart badge to show '2', but got '{badge_text}'"

        # ------------------------------------------------------------
        # STEP 5: Hover over cart icon and verify mini‑summary
        # ------------------------------------------------------------
        cart_icon_selector = "#cart-icon"
        await page.hover(cart_icon_selector)
        # Wait for the mini‑summary tooltip/popup to appear
        mini_summary_selector = "#cart-mini-summary"
        mini_summary_element = await page.wait_for_selector(mini_summary_selector)
        mini_summary_text = await mini_summary_element.inner_text()
        # Verify both product names appear in the summary
        assert "Product 1" in mini_summary_text, "Mini‑summary missing 'Product 1'"
        assert "Product 2" in mini_summary_text, "Mini‑summary missing 'Product 2'"

        # ------------------------------------------------------------
        # Cleanup
        # ------------------------------------------------------------
        await context.close()
        await browser.close()

asyncio.run(run())
