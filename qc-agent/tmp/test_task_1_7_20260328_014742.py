import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Test: Verify Responsive Layout at Desktop Breakpoint (≥1024px)
# Steps:
#   1. Resize browser window to 1280px width.
#   2. Verify header, footer, and main content adopt the desktop grid layout.
#   3. Verify process steps are displayed horizontally.
#   4. Verify field groups use multi‑column arrangement.
# ---------------------------------------------------------------------------

# NOTE: Replace `TARGET_URL` with the actual URL of the Service Catalog page.
TARGET_URL = "https://your-application-domain.com/service-catalog"

async def run_test():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        # Navigate to the Service Catalog page
        await page.goto(TARGET_URL)
        await page.wait_for_load_state("networkidle")

        # -------------------------------------------------------------------
        # 1. Verify the viewport size is set to 1280px width (desktop breakpoint)
        # -------------------------------------------------------------------
        viewport = page.viewport_size
        assert viewport["width"] >= 1024, f"Viewport width {viewport['width']} is less than 1024px"

        # -------------------------------------------------------------------
        # 2. Verify header, footer, and main content adopt the desktop grid layout
        # -------------------------------------------------------------------
        # Assuming the layout uses CSS Grid with a specific grid-template-areas or columns.
        # Adjust selectors according to the actual DOM structure.
        header = page.locator("header")
        footer = page.locator("footer")
        main_content = page.locator("main")

        # Example checks – you may need to adapt the CSS property names.
        await expect(header).to_be_visible()
        await expect(footer).to_be_visible()
        await expect(main_content).to_be_visible()

        # Verify that the main container uses a grid layout with at least two columns
        main_grid_template = await page.evaluate("el => getComputedStyle(el).gridTemplateColumns", await main_content.element_handle())
        assert main_grid_template != "none", "Main content does not use CSS Grid layout"
        # Simple heuristic: ensure there are at least two column definitions (e.g., "1fr 1fr")
        column_count = len([c for c in main_grid_template.split() if c.strip()])
        assert column_count >= 2, f"Expected at least 2 grid columns, found {column_count}"

        # -------------------------------------------------------------------
        # 3. Verify process steps are displayed horizontally
        # -------------------------------------------------------------------
        # Assuming process steps are inside an element with a data-test-id or class like `.process-steps`
        process_steps = page.locator(".process-steps")
        await expect(process_steps).to_be_visible()
        # Check that the container uses flexbox or grid with a row direction
        display_type = await page.evaluate(
            "el => getComputedStyle(el).display",
            await process_steps.element_handle()
        )
        flex_direction = await page.evaluate(
            "el => getComputedStyle(el).flexDirection",
            await process_steps.element_handle()
        )
        grid_auto_flow = await page.evaluate(
            "el => getComputedStyle(el).gridAutoFlow",
            await process_steps.element_handle()
        )
        # Acceptable horizontal layouts: flex row or grid auto-flow column
        horizontal = (
            (display_type == "flex" and flex_direction.startswith("row")) or
            (display_type == "grid" and grid_auto_flow == "column")
        )
        assert horizontal, "Process steps are not arranged horizontally"

        # -------------------------------------------------------------------
        # 4. Verify field groups use multi‑column arrangement
        # -------------------------------------------------------------------
        # Assuming each field group has a class like `.field-group`
        field_groups = page.locator(".field-group")
        count = await field_groups.count()
        assert count > 0, "No field groups found on the page"
        for i in range(count):
            group = field_groups.nth(i)
            await expect(group).to_be_visible()
            # Check that the group uses a grid with more than one column
            group_grid_template = await page.evaluate(
                "el => getComputedStyle(el).gridTemplateColumns",
                await group.element_handle()
            )
            col_defs = [c for c in group_grid_template.split() if c.strip()]
            assert len(col_defs) > 1, f"Field group {i+1} does not use multi‑column layout"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
