import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – replace with the actual URL of the login page you want to test
# ---------------------------------------------------------------------------
LOGIN_URL = "https://your-application-domain.com/login"

# Selectors – adjust if your application uses different attribute names or structures
USERNAME_INPUT = "input[name=\"username\"]"
PASSWORD_INPUT = "input[name=\"password\"]"
LOGIN_BUTTON = "button:has-text(\"Login\")"

# Expected style values – update according to your style guide specifications
EXPECTED_STYLES = {
    "font_family": "Arial, Helvetica, sans-serif",
    "font_size": "16px",
    "color": "rgb(33, 33, 33)",  # example: dark gray text color
    "border_radius": "4px",
    "border_color": "rgb(200, 200, 200)",  # light gray border
    "button_bg_color": "rgb(0, 123, 255)",   # primary brand color
    "button_text_color": "rgb(255, 255, 255)",
    "button_hover_bg_color": "rgb(0, 105, 217)"  # slightly darker shade on hover
}

async def get_computed_style(page, selector, property_name):
    """Utility to fetch a computed CSS property for a given selector."""
    return await page.evaluate(
        "(selector, prop) => {
            const el = document.querySelector(selector);
            if (!el) { return null; }
            const style = window.getComputedStyle(el);
            return style.getPropertyValue(prop);
        }",
        selector,
        property_name,
    )

async def verify_input_field_styles(page, selector):
    # Font family
    font_family = await get_computed_style(page, selector, "font-family")
    assert EXPECTED_STYLES["font_family"] in font_family, f"Font family mismatch for {selector}: expected '{EXPECTED_STYLES['font_family']}', got '{font_family}'"

    # Font size
    font_size = await get_computed_style(page, selector, "font-size")
    assert font_size == EXPECTED_STYLES["font_size"], f"Font size mismatch for {selector}: expected {EXPECTED_STYLES['font_size']}, got {font_size}"

    # Text color
    color = await get_computed_style(page, selector, "color")
    assert color == EXPECTED_STYLES["color"], f"Text color mismatch for {selector}: expected {EXPECTED_STYLES['color']}, got {color}"

    # Border radius
    border_radius = await get_computed_style(page, selector, "border-radius")
    assert border_radius == EXPECTED_STYLES["border_radius"], f"Border radius mismatch for {selector}: expected {EXPECTED_STYLES['border_radius']}, got {border_radius}"

    # Border color (assuming solid border)
    border_color = await get_computed_style(page, selector, "border-color")
    assert border_color == EXPECTED_STYLES["border_color"], f"Border color mismatch for {selector}: expected {EXPECTED_STYLES['border_color']}, got {border_color}"

async def verify_button_styles(page, selector):
    # Background color
    bg_color = await get_computed_style(page, selector, "background-color")
    assert bg_color == EXPECTED_STYLES["button_bg_color"], f"Button background color mismatch: expected {EXPECTED_STYLES['button_bg_color']}, got {bg_color}"

    # Text color
    txt_color = await get_computed_style(page, selector, "color")
    assert txt_color == EXPECTED_STYLES["button_text_color"], f"Button text color mismatch: expected {EXPECTED_STYLES['button_text_color']}, got {txt_color}"

    # Hover state – trigger hover and re‑evaluate background color
    await page.hover(selector)
    hover_bg_color = await get_computed_style(page, selector, "background-color")
    assert hover_bg_color == EXPECTED_STYLES["button_hover_bg_color"], (
        f"Button hover background color mismatch: expected {EXPECTED_STYLES['button_hover_bg_color']}, got {hover_bg_color}"
    )

async def run_test():
    async with async_playwright() as p:
        # Choose the browser you prefer – here we use Chromium in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(LOGIN_URL)

        # Verify visual consistency of username input field
        await verify_input_field_styles(page, USERNAME_INPUT)
        # Verify visual consistency of password input field
        await verify_input_field_styles(page, PASSWORD_INPUT)
        # Verify visual consistency of the Login button (normal & hover states)
        await verify_button_styles(page, LOGIN_BUTTON)

        print("✅ Visual consistency verification passed.")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
