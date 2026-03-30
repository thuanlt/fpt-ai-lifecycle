import asyncio
from playwright.async_api import async_playwright, expect

BASE_URL = "https://example.com"  # Replace with the actual application URL
SEARCH_QUERY = "espresso machine"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the home page
        await page.goto(BASE_URL)

        # --- Step 1: Enter search query and submit ---
        # Adjust selectors according to the actual application
        await page.fill('input[name="search"]', SEARCH_QUERY)
        await page.click('button[type="submit"]')

        # Wait for the results container to appear
        await page.wait_for_selector('.product-item')

        # --- Step 2: Verify that at least one product is displayed ---
        product_items = await page.query_selector_all('.product-item')
        assert product_items, "No products were returned for the query"

        # --- Step 3: Validate each product entry ---
        for idx, item in enumerate(product_items, start=1):
            # Title and description validation
            title_el = await item.query_selector('.product-title')
            desc_el = await item.query_selector('.product-description')
            title_text = (await title_el.inner_text()).lower() if title_el else ""
            desc_text = (await desc_el.inner_text()).lower() if desc_el else ""
            assert (
                SEARCH_QUERY.lower() in title_text or SEARCH_QUERY.lower() in desc_text
            ), f"Product #{idx} does not contain the search term in title or description"

            # Image presence validation
            img_el = await item.query_selector('.product-image img')
            assert img_el, f"Product #{idx} is missing an image"

            # Price validation
            price_el = await item.query_selector('.product-price')
            price_text = await price_el.inner_text() if price_el else ""
            assert price_text.strip(), f"Product #{idx} is missing a price"

            # "Add to Cart" button validation
            add_btn = await item.query_selector('button.add-to-cart')
            assert add_btn, f"Product #{idx} is missing an 'Add to Cart' button"

        # --- Step 4: Verify pagination controls appear when needed ---
        pagination_el = await page.query_selector('.pagination')
        if pagination_el:
            # Simple visibility check – more detailed pagination logic can be added as needed
            assert await pagination_el.is_visible(), "Pagination controls are present but not visible"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
