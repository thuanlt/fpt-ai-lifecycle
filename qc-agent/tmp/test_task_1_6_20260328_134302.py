import asyncio
from playwright.async_api import async_playwright

# Adjust these constants to match your application
LOGIN_URL = "https://example.com/login"  # <-- replace with actual login page URL
LOGO_SELECTOR = "#logo"                # <-- replace with the actual selector for the logo element

# Viewport definitions (width, height)
VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet":  {"width": 768,  "height": 1024},
    "mobile":  {"width": 375,  "height": 667}
}

# Tolerance for aspect‑ratio comparison (e.g., 1% deviation)
ASPECT_RATIO_TOLERANCE = 0.01

async def get_logo_bbox(page):
    """Return the bounding box (x, y, width, height) of the logo element."""
    element = await page.wait_for_selector(LOGO_SELECTOR, state="visible", timeout=5000)
    return await element.bounding_box()

def aspect_ratio(width: float, height: float) -> float:
    return width / height if height != 0 else 0

async def verify_logo_scaling():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # set headless=True for CI
        reference_aspect = None
        reference_width = None

        for name, vp in VIEWPORTS.items():
            context = await browser.new_context(viewport=vp)
            page = await context.new_page()
            await page.goto(LOGIN_URL)

            bbox = await get_logo_bbox(page)
            if not bbox:
                raise AssertionError(f"Logo not found on {name} viewport")

            width, height = bbox["width"], bbox["height"]
            current_aspect = aspect_ratio(width, height)

            print(f"[{name}] Logo size: {width:.2f}×{height:.2f} (aspect={current_aspect:.4f})")

            # Verify aspect ratio consistency
            if reference_aspect is None:
                reference_aspect = current_aspect
                reference_width = width
            else:
                diff = abs(current_aspect - reference_aspect)
                assert diff <= ASPECT_RATIO_TOLERANCE, (
                    f"Aspect ratio deviates on {name} viewport (diff={diff:.4f})"
                )
                # Verify that the logo gets smaller on smaller viewports
                if vp["width"] < VIEWPORTS["desktop"]["width"]:
                    assert width < reference_width, (
                        f"Logo width not reduced on {name} viewport (width={width}, "
                        f"reference={reference_width})"
                    )

            await context.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_logo_scaling())
