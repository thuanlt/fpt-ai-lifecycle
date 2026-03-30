import asyncio
from playwright.async_api import async_playwright

# Configuration
PROFILE_URL = "https://your-app-domain.com/profile"  # <-- replace with actual URL
EXPECTED_BORDER_RADIUS_PX = "8px"  # Design system specifies 8dp, typically rendered as 8px in web

# Selectors for UI components to validate
SELECTORS = {
    "buttons": "button",
    "input_fields": "input",
    "cards": ".card"  # Adjust if your card component uses a different class/selector
}

async def check_border_radius(page, selector_name, selector):
    elements = await page.query_selector_all(selector)
    if not elements:
        print(f"[WARN] No elements found for selector '{selector_name}' ({selector})")
        return True  # No elements to check; treat as pass
    all_match = True
    for idx, el in enumerate(elements, start=1):
        # Retrieve the computed border-radius value
        border_radius = await el.evaluate("el => getComputedStyle(el).borderRadius")
        if border_radius != EXPECTED_BORDER_RADIUS_PX:
            print(
                f"[FAIL] {selector_name} #{idx} (selector: '{selector}') has border-radius "
                f"'{border_radius}' (expected: '{EXPECTED_BORDER_RADIUS_PX}')"
            )
            all_match = False
        else:
            print(
                f"[PASS] {selector_name} #{idx} (selector: '{selector}') border-radius matches "
                f"'{EXPECTED_BORDER_RADIUS_PX}'"
            )
    return all_match

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Profile screen
        await page.goto(PROFILE_URL)
        await page.wait_for_load_state("networkidle")

        # Perform border‑radius checks for each component group
        overall_success = True
        for name, sel in SELECTORS.items():
            result = await check_border_radius(page, name, sel)
            overall_success = overall_success and result

        await browser.close()
        if overall_success:
            print("\n=== ALL COMPONENTS MATCH THE DESIGN SYSTEM SPECIFICATION ===")
        else:
            print("\n=== ONE OR MORE COMPONENTS DO NOT MATCH THE DESIGN SYSTEM SPECIFICATION ===")

if __name__ == "__main__":
    asyncio.run(run_test())
