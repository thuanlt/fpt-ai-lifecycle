import asyncio
from playwright.async_api import async_playwright, expect

# Configuration
BASE_URL = "http://localhost:3000/service-catalog"  # <-- replace with actual URL
GROUP_TITLE_TEXT = "Contact Information"
# Expected design tokens (example values – adjust to match your design system)
EXPECTED_FONT_SIZE_PX = 18
EXPECTED_FONT_WEIGHT = "600"  # typically "bold" or numeric weight
EXPECTED_SPACING_PX = 16  # vertical spacing between fields

async def verify_group_title_typography(page):
    """Verify that the group title uses the correct typography."""
    title = page.locator(f"text={GROUP_TITLE_TEXT}")
    await expect(title).to_be_visible()
    # Retrieve computed styles via JavaScript
    styles = await title.evaluate("el => getComputedStyle(el)")
    font_size = float(styles["fontSize"].replace('px', ''))
    font_weight = styles["fontWeight"]
    assert font_size == EXPECTED_FONT_SIZE_PX, f"Expected font size {EXPECTED_FONT_SIZE_PX}px, got {font_size}px"
    assert font_weight == EXPECTED_FONT_WEIGHT, f"Expected font weight {EXPECTED_FONT_WEIGHT}, got {font_weight}"

async def verify_fields_layout(page, is_mobile: bool):
    """Verify fields are laid out according to the grid system.
    Desktop → two columns, Mobile → single column.
    """
    # Locate the container that holds the group title and its fields
    container = page.locator(f"section:has-text('{GROUP_TITLE_TEXT}')")
    await expect(container).to_be_visible()
    # All form controls inside the container (inputs, selects, textareas)
    fields = container.locator("input, select, textarea")
    count = await fields.count()
    assert count > 0, "No form fields found inside the group container"

    # Gather the x‑coordinates of each field's bounding box
    x_positions = []
    for i in range(count):
        box = await fields.nth(i).bounding_box()
        x_positions.append(round(box["x"]))

    # Determine unique column positions (allow a small tolerance)
    tolerance = 5
    unique_columns = []
    for x in x_positions:
        if not any(abs(x - col) <= tolerance for col in unique_columns):
            unique_columns.append(x)
    column_count = len(unique_columns)

    if is_mobile:
        expected_columns = 1
    else:
        expected_columns = 2
    assert column_count == expected_columns, (
        f"Expected {expected_columns} column(s) for {'mobile' if is_mobile else 'desktop'} view, "
        f"but found {column_count}. X positions: {x_positions}"
    )

    # Verify vertical spacing between consecutive fields matches the design token
    # Sort fields by their y coordinate to evaluate vertical gaps
    boxes = []
    for i in range(count):
        boxes.append(await fields.nth(i).bounding_box())
    boxes.sort(key=lambda b: b["y"])  # top‑to‑bottom order
    for i in range(len(boxes) - 1):
        gap = boxes[i + 1]["y"] - (boxes[i]["y"] + boxes[i]["height"])  # space between bottom of one and top of next
        # Allow a small deviation (+/- 2px)
        assert abs(gap - EXPECTED_SPACING_PX) <= 2, (
            f"Vertical spacing between field {i} and {i+1} is {gap}px, "
            f"expected ~{EXPECTED_SPACING_PX}px"
        )

async def run_test():
    async with async_playwright() as p:
        # Choose Chromium (you can switch to firefox/webkit if needed)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------- Desktop view (>= 1024px) ----------
        await page.set_viewport_size({"width": 1280, "height": 800})
        await page.goto(BASE_URL)
        await verify_group_title_typography(page)
        await verify_fields_layout(page, is_mobile=False)

        # ---------- Mobile view (<= 375px) ----------
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.reload()
        await verify_group_title_typography(page)
        await verify_fields_layout(page, is_mobile=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
