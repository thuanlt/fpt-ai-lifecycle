import asyncio
from playwright.async_api import async_playwright, expect

# Adjust this URL to point to the Service Catalog page under test
SERVICE_CATALOG_URL = "http://localhost:3000/service-catalog"

async def run_test():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 800, "height": 600})
        page = await context.new_page()

        # Navigate to the Service Catalog page
        await page.goto(SERVICE_CATALOG_URL)
        await page.wait_for_load_state("networkidle")

        # ---------------------------------------------------------------------
        # Step 1: Verify that the header collapses to a hamburger menu while the logo remains visible
        # ---------------------------------------------------------------------
        header = page.locator("header")
        hamburger = header.locator("button[aria-label='Menu'], button.hamburger, .hamburger-menu")
        logo = header.locator("img.logo, .logo")

        # The hamburger menu should be visible at the tablet breakpoint
        await expect(hamburger).to_be_visible(timeout=5000)
        # The logo should still be visible
        await expect(logo).to_be_visible(timeout=5000)

        # ---------------------------------------------------------------------
        # Step 2: Verify that process steps switch to a stacked vertical layout
        # ---------------------------------------------------------------------
        process_steps = page.locator(".process-steps, #process-steps")
        # Ensure the container is present
        await expect(process_steps).to_be_visible(timeout=5000)
        # Check that the CSS flex-direction (or grid) indicates a vertical stack
        flex_direction = await process_steps.evaluate("el => getComputedStyle(el).flexDirection")
        grid_template_rows = await process_steps.evaluate("el => getComputedStyle(el).gridTemplateRows")
        # Accept either flex column or a single column grid as vertical stacking
        assert flex_direction == "column" or grid_template_rows != "none", \
            "Process steps are not stacked vertically"

        # ---------------------------------------------------------------------
        # Step 3: Verify that field groups adjust to a two‑column layout with reduced spacing
        # ---------------------------------------------------------------------
        field_group = page.locator(".field-group, .field-group-container")
        await expect(field_group).to_be_visible(timeout=5000)
        # Verify that the layout uses two columns (grid-template-columns or flex wrap)
        columns = await field_group.evaluate(
            "el => getComputedStyle(el).gridTemplateColumns || getComputedStyle(el).flexWrap"
        )
        # Simple heuristic: gridTemplateColumns should contain two tracks (e.g., '1fr 1fr')
        is_two_column = False
        if columns:
            if "gridTemplateColumns" in columns:
                is_two_column = len(columns.split()) == 2
            else:
                # If using flex, ensure wrap is enabled and items are roughly half width
                is_two_column = True
        assert is_two_column, "Field groups are not displayed in a two‑column layout"

        # Optionally, verify reduced spacing (e.g., gap or margin)
        gap = await field_group.evaluate("el => getComputedStyle(el).gap || getComputedStyle(el).columnGap")
        # Assuming the design defines a reduced gap at tablet size (e.g., <= 24px)
        if gap:
            gap_value = float(gap.replace('px', '').strip())
            assert gap_value <= 24, f"Unexpected spacing between columns: {gap_value}px"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
