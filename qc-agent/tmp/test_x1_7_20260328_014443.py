import asyncio
from playwright.async_api import async_playwright, expect

# Adjust this URL to point to the actual homepage of the application under test.
HOME_URL = "http://localhost:3000"

async def run_test():
    async with async_playwright() as p:
        # Launch Chromium browser (headless can be set to True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Load the homepage
        await page.goto(HOME_URL)
        await page.wait_for_load_state("domcontentloaded")

        # Verify the search input field with the correct placeholder is visible
        search_input = page.locator('input[placeholder="Search products..."]')
        await expect(search_input).to_be_visible()
        # Additional check: ensure the placeholder attribute matches exactly
        placeholder_value = await search_input.get_attribute("placeholder")
        assert placeholder_value == "Search products...", (
            f"Expected placeholder 'Search products...' but got '{placeholder_value}'"
        )

        # Verify the magnifying glass icon button is positioned to the right of the input
        # Assuming the button has an accessible name or aria-label; adjust selector as needed.
        # Here we look for a button that contains an <svg> (common for icon buttons).
        search_button = page.locator('button:has(svg)')
        await expect(search_button).to_be_visible()

        # Optionally, verify the button is located to the right of the input field.
        # This can be done by comparing bounding boxes.
        input_box = await search_input.bounding_box()
        button_box = await search_button.bounding_box()
        assert input_box is not None and button_box is not None, "Could not retrieve element positions"
        assert button_box["x"] > input_box["x"] + input_box["width"], (
            "Search button is not positioned to the right of the input field"
        )

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
