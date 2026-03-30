import asyncio
from playwright.async_api import async_playwright, expect

# Replace this URL with the actual Service Catalog page URL
TARGET_URL = "https://your-application-domain.com/service-catalog"

async def verify_responsive_layout(page):
    # Resize viewport to mobile breakpoint (375px width)
    await page.set_viewport_size({"width": 375, "height": 800})

    # Verify header shows only logo and hamburger icon
    logo = page.locator("header .logo")
    hamburger = page.locator("header .hamburger-icon")
    other_header_items = page.locator("header :not(.logo):not(.hamburger-icon)")

    await expect(logo).to_be_visible()
    await expect(hamburger).to_be_visible()
    await expect(other_header_items).to_have_count(0)

    # Verify all main sections stack vertically
    sections = [
        page.locator("header"),
        page.locator("section.process-steps"),
        page.locator("section.fields"),
        page.locator("footer")
    ]
    previous_bottom = None
    for sec in sections:
        await expect(sec).to_be_visible()
        box = await sec.bounding_box()
        if previous_bottom is not None:
            # Ensure current section starts below the previous one
            assert box["y"] >= previous_bottom, "Sections are not stacked vertically"
        previous_bottom = box["y"] + box["height"]

    # Verify touch targets meet minimum size (48x48 dp)
    touch_targets = page.locator("a, button, [role='button'], input[type='checkbox'], input[type='radio']")
    count = await touch_targets.count()
    for i in range(count):
        element = touch_targets.nth(i)
        box = await element.bounding_box()
        assert box["width"] >= 48 and box["height"] >= 48, f"Touch target too small: {await element.get_attribute('outerHTML')}"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(TARGET_URL)
        await verify_responsive_layout(page)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
