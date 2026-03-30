import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to Service Catalog main page (replace with actual URL if different)
        await page.goto("http://localhost:3000/service-catalog")

        # ---------- Header Visibility & Position ----------
        header = page.locator("header")
        await expect(header).to_be_visible()
        header_box = await header.bounding_box()
        # Header should be at the very top of the viewport (y ≈ 0)
        assert header_box["y"] == 0, f"Header y position is {header_box['y']}, expected 0"
        # Header height should match design spec (64px ±1px tolerance)
        assert abs(header_box["height"] - 64) <= 1, f"Header height {header_box['height']} != 64px"
        # Background color should match design system (adjust expected value as needed)
        bg_color = await header.evaluate("el => getComputedStyle(el).backgroundColor")
        expected_bg = "rgb(255, 255, 255)"  # placeholder – replace with actual design token
        assert bg_color == expected_bg, f"Header background {bg_color} != {expected_bg}"

        # ---------- Logo Alignment (Left) ----------
        logo = page.locator(".logo")
        await expect(logo).to_be_visible()
        logo_box = await logo.bounding_box()
        # Logo's left edge should be at or very near the header's left edge
        assert logo_box["x"] >= header_box["x"], "Logo is not aligned to the left edge of the header"

        # ---------- Navigation Links Alignment (Center) ----------
        nav = page.locator(".nav-links")
        await expect(nav).to_be_visible()
        nav_box = await nav.bounding_box()
        header_center_x = header_box["x"] + header_box["width"] / 2
        nav_center_x = nav_box["x"] + nav_box["width"] / 2
        # Allow a small pixel tolerance for centering
        assert abs(header_center_x - nav_center_x) < 5, "Navigation links are not horizontally centered within the header"

        # ---------- User Profile Icon Alignment (Right) ----------
        profile = page.locator(".profile-icon")
        await expect(profile).to_be_visible()
        profile_box = await profile.bounding_box()
        header_right_x = header_box["x"] + header_box["width"]
        # Profile icon's right edge should be at or very near the header's right edge
        assert profile_box["x"] + profile_box["width"] <= header_right_x, "Profile icon is not aligned to the right edge of the header"

        # Clean up
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
