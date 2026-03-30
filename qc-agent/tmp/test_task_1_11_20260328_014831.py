import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Test: Verify Dark Mode Rendering for Service Catalog UI
# ---------------------------------------------------------------------------
# Steps:
# 1. Navigate to the Service Catalog application.
# 2. Switch the application to Dark mode via user settings.
# 3. Verify that all major UI components (header, footer, process steps,
#    form fields, help texts) adapt to Dark theme colors.
# 4. Verify that text remains readable and contrast meets WCAG AA.
# ---------------------------------------------------------------------------

# NOTE: Replace the placeholder URLs and selectors with the actual values
# from the target application before running the script.

BASE_URL = "https://your-application-url.com/service-catalog"  # <-- Update

# Selectors – adjust according to the real DOM structure
SELECTORS = {
    "user_menu_button": "button#user-menu",          # Opens user settings menu
    "settings_option": "a[href*='settings']",       # Link to settings page
    "dark_mode_toggle": "input#dark-mode-toggle",   # Checkbox or switch for dark mode
    "header": "header.site-header",
    "footer": "footer.site-footer",
    "process_steps": "section.process-steps",
    "form_fields": "form >> input, form >> textarea, form >> select",
    "help_texts": "[data-help-text]",
}

# Helper function to compute contrast ratio (simplified version)
def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return r, g, b

def luminance(r, g, b):
    a = [r, g, b]
    for i in range(3):
        if a[i] <= 0.03928:
            a[i] = a[i] / 12.92
        else:
            a[i] = ((a[i] + 0.055) / 1.055) ** 2.4
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]

def contrast_ratio(lum1, lum2):
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

async def verify_dark_mode(page):
    # Verify background colors are dark and text colors are light enough
    components = [
        SELECTORS["header"],
        SELECTORS["footer"],
        SELECTORS["process_steps"],
        SELECTORS["form_fields"],
        SELECTORS["help_texts"],
    ]

    for selector in components:
        elements = await page.query_selector_all(selector)
        for element in elements:
            # Get computed background and color styles
            bg_color = await element.evaluate("el => getComputedStyle(el).backgroundColor")
            text_color = await element.evaluate("el => getComputedStyle(el).color")

            # Convert rgb(a) to hex for contrast calculation
            def rgb_to_hex(rgb_str: str) -> str:
                # Handles formats like 'rgb(34, 34, 34)' or 'rgba(34,34,34,1)'
                parts = rgb_str.replace('rgba', '').replace('rgb', '').replace('(', '').replace(')', '').split(',')
                r, g, b = [int(p.strip()) for p in parts[:3]]
                return f"#{r:02x}{g:02x}{b:02x}"

            bg_hex = rgb_to_hex(bg_color)
            txt_hex = rgb_to_hex(text_color)
            bg_lum = luminance(*hex_to_rgb(bg_hex))
            txt_lum = luminance(*hex_to_rgb(txt_hex))
            ratio = contrast_ratio(bg_lum, txt_lum)

            # WCAG AA requires a contrast ratio of at least 4.5:1 for normal text
            assert ratio >= 4.5, f"Contrast ratio {ratio:.2f} is below WCAG AA threshold for element {selector}"

            # Additionally, ensure background is dark (luminosity < 0.5) and text is light (> 0.5)
            assert bg_lum < 0.5, f"Background of {selector} is not dark enough (luminosity={bg_lum:.2f})"
            assert txt_lum > 0.5, f"Text of {selector} is not light enough (luminosity={txt_lum:.2f})"

async def run():
    async with async_playwright() as p:
        # Choose the browser you prefer (chromium, firefox, webkit)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Navigate to Service Catalog page
        await page.goto(BASE_URL)
        await page.wait_for_load_state("networkidle")

        # 2. Open user settings and enable Dark Mode
        # Click user menu
        await page.click(SELECTORS["user_menu_button"])
        # Click Settings option
        await page.click(SELECTORS["settings_option"])
        await page.wait_for_load_state("networkidle")
        # Toggle Dark Mode (assumes a checkbox input)
        dark_mode_checkbox = await page.wait_for_selector(SELECTORS["dark_mode_toggle"])
        # If not already checked, click to enable
        is_checked = await dark_mode_checkbox.is_checked()
        if not is_checked:
            await dark_mode_checkbox.check()
        # Wait for UI to apply theme (adjust timeout as needed)
        await page.wait_for_timeout(2000)

        # 3. Verify UI components adapt to Dark theme colors and meet contrast requirements
        await verify_dark_mode(page)

        print("✅ Dark mode rendering verification passed.")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
