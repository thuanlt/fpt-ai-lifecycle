import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these selectors according to the actual application under test
CART_ITEM_SELECTOR = "css=.cart-item"  # Container for a cart line item
REMOVE_ICON_SELECTOR = "css=.cart-item .remove-icon"  # Remove (trash) icon inside a cart item
CART_TOTAL_SELECTOR = "css=.cart-total"  # Element that displays the cart total amount
TOAST_SELECTOR = "css=.toast-message"  # Toast notification element

async def verify_item_removed(page, item_index: int):
    """Verify that the cart item at the given index is no longer present.
    Args:
        page: Playwright page instance.
        item_index: Zero‑based index of the item that should have been removed.
    """
    # Get the list of current cart items
    items = await page.query_selector_all(CART_ITEM_SELECTOR)
    # The removed item's index should now be out of range
    assert len(items) <= item_index, f"Item at index {item_index} still present in cart"

async def get_cart_total(page) -> float:
    """Extract the numeric cart total from the UI.
    Returns:
        The cart total as a float.
    """
    total_text = await page.inner_text(CART_TOTAL_SELECTOR)
    # Assuming the total is formatted like "$123.45" – strip non‑numeric characters
    import re
    numeric = re.sub(r"[^0-9.]", "", total_text)
    return float(numeric) if numeric else 0.0

async def main():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # -----------------------------------------------------------------
        # PRECONDITIONS – navigate to the shopping cart page where items exist
        # -----------------------------------------------------------------
        await page.goto("https://your‑application.example.com/cart")
        # Wait for cart items to be visible
        await page.wait_for_selector(CART_ITEM_SELECTOR)

        # Capture initial state for verification
        initial_items = await page.query_selector_all(CART_ITEM_SELECTOR)
        if not initial_items:
            raise Exception("No cart items found – cannot perform removal test")
        # Choose the first item (index 0) for removal
        item_to_remove_index = 0
        item_to_remove = initial_items[item_to_remove_index]
        # Record the total before removal
        total_before = await get_cart_total(page)

        # ---------------------------------------------------------------
        # STEP 1: Click the "Remove" (trash) icon for the chosen cart line item
        # ---------------------------------------------------------------
        remove_icon = await item_to_remove.query_selector(REMOVE_ICON_SELECTOR)
        if not remove_icon:
            raise Exception("Remove icon not found within the selected cart item")
        await remove_icon.click()

        # ---------------------------------------------------------------
        # EXPECTED RESULT 1: The item disappears from the cart list
        # ---------------------------------------------------------------
        await page.wait_for_timeout(500)  # small wait for UI animation
        await verify_item_removed(page, item_to_remove_index)

        # ---------------------------------------------------------------
        # EXPECTED RESULT 2: Cart total recalculates to exclude the removed item
        # ---------------------------------------------------------------
        total_after = await get_cart_total(page)
        assert total_after < total_before, (
            f"Cart total was not reduced after removal. Before: {total_before}, After: {total_after}"
        )

        # ---------------------------------------------------------------
        # EXPECTED RESULT 3: A toast "Item removed" is displayed
        # ---------------------------------------------------------------
        toast = await page.wait_for_selector(TOAST_SELECTOR, timeout=3000)
        toast_text = await toast.inner_text()
        assert "Item removed" in toast_text, f"Expected toast message not found. Got: '{toast_text}'"

        print("✅ Test case passed: Remove item from cart")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
