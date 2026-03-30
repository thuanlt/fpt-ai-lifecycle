import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual application URL
        await page.goto("http://localhost:3000")

        # Locate a paragraph element inside a content card
        # Adjust the selector according to the real DOM structure
        paragraph = await page.wait_for_selector(".content-card p")

        # Retrieve computed CSS properties
        font_family = await paragraph.evaluate("el => getComputedStyle(el).fontFamily")
        font_size = await paragraph.evaluate("el => getComputedStyle(el).fontSize")
        color = await paragraph.evaluate("el => getComputedStyle(el).color")

        # Assertions based on the design system specifications
        assert "Roboto" in font_family, f"Expected font family to include 'Roboto', got {font_family}"
        assert font_size == "14px", f"Expected font size 14px, got {font_size}"
        # Replace the expected_color with the actual value of the onSurface token (e.g., rgb(...))
        expected_color = "rgb(0, 0, 0)"  # placeholder for onSurface token
        assert color == expected_color, f"Expected text color {expected_color}, got {color}"

        await browser.close()

asyncio.run(run())
