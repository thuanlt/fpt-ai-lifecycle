import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch Chromium browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        # Create a new browser context with a desktop viewport (>1024px width)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        # TODO: Replace with the actual URL of the application under test
        await page.goto("http://localhost")

        # Ensure the viewport is set to desktop dimensions (redundant but explicit)
        await page.set_viewport_size({"width": 1280, "height": 800})

        # ---------------------------------------------------------------------
        # Validate that the H1 heading scales to the desktop token value (32px)
        # ---------------------------------------------------------------------
        h1_font_size = await page.evaluate(
            "() => {
                const el = document.querySelector('h1');
                return el ? getComputedStyle(el).fontSize : null;
            }"
        )
        assert h1_font_size == "32px", f"Expected H1 font size to be 32px, but got {h1_font_size}"

        # ---------------------------------------------------------------
        # Validate that body text respects the line‑height token (non‑empty)
        # ---------------------------------------------------------------
        body_line_height = await page.evaluate(
            "() => {
                const el = document.querySelector('p');
                return el ? getComputedStyle(el).lineHeight : null;
            }"
        )
        assert body_line_height is not None and body_line_height != "", (
            "Body paragraph line-height should be defined according to the design token"
        )

        # Clean up
        await browser.close()

asyncio.run(run())
