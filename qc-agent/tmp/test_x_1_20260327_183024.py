import asyncio
from playwright.async_api import async_playwright

# Expected primary color hex value as defined in the design system
EXPECTED_PRIMARY_COLOR = "#1A73E8"  # <-- replace with actual hex from design system

async def verify_primary_button_color(page):
    # Wait for the primary button to be visible on the Home screen
    # Adjust the selector to match the actual primary button implementation
    primary_button = await page.wait_for_selector("button.primary", timeout=5000)
    # Retrieve the computed background color of the button
    bg_color = await page.evaluate(
        "element => getComputedStyle(element).backgroundColor",
        primary_button
    )
    # Convert the RGB(A) string to hex for comparison
    def rgb_to_hex(rgb_str: str) -> str:
        # Handles formats like "rgb(26, 115, 232)" or "rgba(26, 115, 232, 1)"
        parts = rgb_str.replace("rgba", "").replace("rgb", "").strip("() ").split(",")
        r, g, b = [int(p.strip()) for p in parts[:3]]
        return f"#{r:02X}{g:02X}{b:02X}".lower()

    actual_hex = rgb_to_hex(bg_color)
    assert actual_hex == EXPECTED_PRIMARY_COLOR.lower(), (
        f"Primary button color mismatch: expected {EXPECTED_PRIMARY_COLOR}, got {actual_hex}"
    )
    print(f"✅ Primary button color verified: {actual_hex}")

async def run_test():
    async with async_playwright() as p:
        # Choose the browser you prefer (chromium, firefox, webkit)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to the application Home screen – replace with actual URL
        await page.goto("http://localhost:3000")
        # Optionally, ensure we are on the Home screen (e.g., by checking a unique element)
        await page.wait_for_selector("h1:has-text('Home')", timeout=5000)
        # Perform the color verification
        await verify_primary_button_color(page)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
