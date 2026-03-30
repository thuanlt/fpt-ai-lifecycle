import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these selectors and URL to match the actual application under test
BASE_URL = "https://example.com"  # <-- replace with the real URL
SEARCH_INPUT_SELECTOR = "#search-input"  # <-- selector for the search text field
SEARCH_BUTTON_SELECTOR = "#search-button"  # <-- selector for the search button
TOOLTIP_SELECTOR = "#tooltip"  # <-- selector for the tooltip that appears on validation error
RESULTS_CONTAINER_SELECTOR = "#results"  # <-- selector for the container that holds search results

async def test_empty_search_query():
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the page containing the search functionality
        await page.goto(BASE_URL)

        # Ensure the search input is empty (clear any pre‑filled value)
        await page.fill(SEARCH_INPUT_SELECTOR, "")

        # Capture the current state of the results container for later comparison
        initial_results_html = await page.inner_html(RESULTS_CONTAINER_SELECTOR)

        # Click the search button while the input is empty
        await page.click(SEARCH_BUTTON_SELECTOR)

        # ---- Expected Result 1: Tooltip appears with correct message ----
        tooltip = page.locator(TOOLTIP_SELECTOR)
        await expect(tooltip).to_be_visible()
        await expect(tooltip).to_have_text("Please enter a search term")

        # ---- Expected Result 2: No navigation occurs (URL stays the same) ----
        await expect(page).to_have_url(BASE_URL)

        # ---- Expected Result 3: Search results area remains unchanged ----
        final_results_html = await page.inner_html(RESULTS_CONTAINER_SELECTOR)
        assert initial_results_html == final_results_html, "Results container changed despite empty query"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_empty_search_query())
