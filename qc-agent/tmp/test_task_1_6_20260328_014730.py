import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # TODO: Replace with the actual URL of the Service Catalog page
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-catalog")

        # ------------------------------------------------------------
        # Selectors – replace with the real selectors from the application
        # ------------------------------------------------------------
        field_selector = "input[name='field-with-help']"   # field that has help text
        tooltip_selector = ".help-tooltip"                # tooltip element

        # -----------------------------------------------------------------
        # Step 1: Hover (or focus) over the field that has associated help text
        # -----------------------------------------------------------------
        await page.hover(field_selector)

        # ------------------------------------------------------------
        # Verify tooltip becomes visible
        # ------------------------------------------------------------
        tooltip = page.locator(tooltip_selector)
        await expect(tooltip).to_be_visible(timeout=3000)

        # ------------------------------------------------------------
        # Verify tooltip text matches the description defined in the SRS
        # ------------------------------------------------------------
        expected_text = "This is the help description for the field."
        actual_text = await tooltip.text_content()
        assert actual_text is not None, "Tooltip text is None"
        assert actual_text.strip() == expected_text, (
            f"Tooltip text mismatch: expected '{expected_text}', got '{actual_text.strip()}'"
        )

        # ------------------------------------------------------------
        # Verify tooltip positioning – it should not overlap the field
        # ------------------------------------------------------------
        field_box = await page.locator(field_selector).bounding_box()
        tooltip_box = await tooltip.bounding_box()
        assert field_box is not None and tooltip_box is not None, "Unable to retrieve bounding boxes"
        # Simple heuristic: tooltip should be to the right or below the field
        overlaps_horizontally = (
            tooltip_box["x"] < field_box["x"] + field_box["width"] and
            tooltip_box["x"] + tooltip_box["width"] > field_box["x"]
        )
        overlaps_vertically = (
            tooltip_box["y"] < field_box["y"] + field_box["height"] and
            tooltip_box["y"] + tooltip_box["height"] > field_box["y"]
        )
        assert not (overlaps_horizontally and overlaps_vertically), "Tooltip overlaps the field"

        # ------------------------------------------------------------
        # Step 2: Move mouse away (or blur) to hide the tooltip
        # ------------------------------------------------------------
        await page.mouse.move(0, 0)  # move to top‑left corner of the viewport
        await expect(tooltip).not_to_be_visible(timeout=3000)

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run())