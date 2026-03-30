import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the application (replace with actual URL)
        await page.goto("http://localhost:3000")

        # ------------------------------------------------------------
        # Test Step 1: Open the Service Creation modal/dialog
        # ------------------------------------------------------------
        # Adjust the selector to match the actual "Create Service" trigger
        await page.click("button#create-service")

        # ------------------------------------------------------------
        # Test Step 2: Enter an invalid version string "v1..0"
        # ------------------------------------------------------------
        await page.fill("input#service-version", "v1..0")

        # ------------------------------------------------------------
        # Test Step 3: Click the Save button
        # ------------------------------------------------------------
        await page.click("button#save-service")

        # ------------------------------------------------------------
        # Expected Result 1: Validation error is displayed
        # ------------------------------------------------------------
        error_locator = page.locator("text=Version must follow semantic versioning (MAJOR.MINOR.PATCH)")
        await expect(error_locator).to_be_visible()

        # ------------------------------------------------------------
        # Expected Result 2: The Service Creation modal remains open
        # ------------------------------------------------------------
        modal_locator = page.locator("#service-modal")
        await expect(modal_locator).to_be_visible()

        # Clean up
        await browser.close()

asyncio.run(run())
