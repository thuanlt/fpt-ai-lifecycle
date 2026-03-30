import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=False)
        # Create a context with an initial viewport; will be resized to tablet width later
        context = await browser.new_context(viewport={"width": 1024, "height": 768})
        page = await context.new_page()
        # TODO: Replace with the actual URL of the application under test
        await page.goto("http://localhost")
        await page.wait_for_load_state("networkidle")

        # ------------------------------------------------------------
        # Step 1: Resize the viewport to a tablet breakpoint (e.g., 800px width)
        # ------------------------------------------------------------
        await page.set_viewport_size({"width": 800, "height": 600})
        # Give the layout a moment to adjust
        await page.wait_for_timeout(500)

        # ------------------------------------------------------------
        # Validation 1: Grid gutters and padding follow the spacing token (16dp)
        # ------------------------------------------------------------
        spacing = await page.evaluate("""
            () => {
                const grid = document.querySelector('.grid-container');
                if (!grid) return null;
                const style = window.getComputedStyle(grid);
                // "gap" is the modern CSS property for grid spacing
                return style.getPropertyValue('gap') || style.getPropertyValue('grid-gap');
            }
        """)
        # The design system defines spacing as 16dp → 16px in CSS
        assert spacing is not None, "Grid container with class '.grid-container' not found."
        assert spacing.strip() == '16px', f"Expected grid spacing of 16px, but got '{spacing}'."

        # ------------------------------------------------------------
        # Validation 2: Components reflow correctly without overlapping or truncation
        # ------------------------------------------------------------
        overlap = await page.evaluate("""
            () => {
                const compA = document.querySelector('.component-a');
                const compB = document.querySelector('.component-b');
                if (!compA || !compB) return false; // If elements missing, treat as no overlap
                const rectA = compA.getBoundingClientRect();
                const rectB = compB.getBoundingClientRect();
                // Determine if rectangles intersect
                const horizontalOverlap = !(rectA.right <= rectB.left || rectA.left >= rectB.right);
                const verticalOverlap = !(rectA.bottom <= rectB.top || rectA.top >= rectB.bottom);
                return horizontalOverlap && verticalOverlap;
            }
        """)
        assert not overlap, "Components .component-a and .component-b overlap after resizing to tablet breakpoint."

        await browser.close()

asyncio.run(run())
