import asyncio
from playwright.async_api import async_playwright, expect

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the application (replace with real URL)
        # ------------------------------------------------------------
        await page.goto("https://example.com/login")
        # ---- Login steps (if authentication is required) ----
        # await page.fill("input[name='username']", "admin")
        # await page.fill("input[name='password']", "password")
        # await page.click("button[type='submit']")
        # await page.wait_for_load_state('networkidle')

        # ------------------------------------------------------------
        # 2. Go to Service Catalog page
        # ------------------------------------------------------------
        await page.goto("https://example.com/service-catalog")
        await page.wait_for_load_state('networkidle')

        # ------------------------------------------------------------
        # 3. Open the "Create New Service" form
        # ------------------------------------------------------------
        await page.click("button#create-service")  # Adjust selector as needed
        # Verify the form is displayed
        await expect(page.locator("form#service-form")).to_be_visible()

        # ------------------------------------------------------------
        # 4. Fill in any data (using a unique name for verification)
        # ------------------------------------------------------------
        service_name = "AutoTestService123"
        await page.fill("input[name='serviceName']", service_name)
        await page.fill("textarea[name='description']", "Test description")

        # ------------------------------------------------------------
        # 5. Click the "Cancel" button
        # ------------------------------------------------------------
        await page.click("button#cancel-service")  # Adjust selector as needed
        # Verify the form is closed / hidden
        await expect(page.locator("form#service-form")).to_be_hidden()

        # ------------------------------------------------------------
        # 6. Search the Service Catalog for the entered name
        # ------------------------------------------------------------
        await page.fill("input#search-box", service_name)
        await page.press("input#search-box", "Enter")
        await page.wait_for_load_state('networkidle')

        # ------------------------------------------------------------
        # 7. Verify that no service with that name exists
        # ------------------------------------------------------------
        # Option A: Look for a "no results" indicator
        no_result = page.locator("text=No services found")
        await expect(no_result).to_be_visible()
        # Option B: Ensure the specific row is absent
        service_row = page.locator(f"text={service_name}")
        await expect(service_row).to_have_count(0)

        # ------------------------------------------------------------
        # Cleanup
        # ------------------------------------------------------------
        await browser.close()

asyncio.run(run())
