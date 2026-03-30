import asyncio
from playwright.async_api import async_playwright, expect

# Expected design system color tokens (replace with actual values from your design system)
EXPECTED_SECONDARY_COLOR = "rgb(0, 123, 255)"          # Default secondary color
EXPECTED_SECONDARY_HOVER_COLOR = "rgb(0, 105, 217)"   # Hover state color
EXPECTED_SECONDARY_ACTIVE_COLOR = "rgb(0, 90, 185)"   # Active (pressed) state color

async def verify_secondary_button_color(page, button_locator):
    # Verify default color
    default_color = await button_locator.evaluate("el => getComputedStyle(el).color")
    assert default_color == EXPECTED_SECONDARY_COLOR, f"Default secondary button color mismatch: expected {EXPECTED_SECONDARY_COLOR}, got {default_color}"

    # Hover and verify hover color
    await button_locator.hover()
    hover_color = await button_locator.evaluate("el => getComputedStyle(el).color")
    assert hover_color == EXPECTED_SECONDARY_HOVER_COLOR, f"Hover secondary button color mismatch: expected {EXPECTED_SECONDARY_HOVER_COLOR}, got {hover_color}"

    # Press (active) and verify active color
    await button_locator.dispatch_event("mousedown")
    active_color = await button_locator.evaluate("el => getComputedStyle(el).color")
    assert active_color == EXPECTED_SECONDARY_ACTIVE_COLOR, f"Active secondary button color mismatch: expected {EXPECTED_SECONDARY_ACTIVE_COLOR}, got {active_color}"
    # Release mouse button
    await button_locator.dispatch_event("mouseup")

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the form screen containing a secondary button
        await page.goto("https://your-application-url.com/form")

        # Locate a secondary action button. Adjust selector according to your app's markup.
        # Example assumes a CSS class "secondary" is used for secondary buttons.
        secondary_button = page.locator("button.secondary")

        # Ensure at least one secondary button exists on the page
        assert await secondary_button.count() > 0, "No secondary button found on the page"

        # Perform the color verification steps
        await verify_secondary_button_color(page, secondary_button.first)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
