import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – replace with the actual URL and selectors for your app
# ---------------------------------------------------------------------------
BASE_URL = "http://your-app-url.com/service-catalog"  # <-- update
DESCRIPTION_SELECTOR = "textarea#description"       # <-- update if different
SAVE_BUTTON_SELECTOR = "button#save"               # <-- update if different
VALIDATION_MESSAGE_TEXT = "Description contains prohibited characters or HTML tags"

async def run() -> None:
    """Execute the validation test for the Description field.

    Steps:
    1. Navigate to the Service Catalog page.
    2. Enter a prohibited HTML tag into the Description field.
    3. Click the Save button.
    4. Verify that the appropriate validation message appears.
    5. Verify that the record is **not** saved (the URL remains unchanged).
    """
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # 1. Open the Service Catalog Management screen
        # ---------------------------------------------------------------
        await page.goto(BASE_URL)

        # ---------------------------------------------------------------
        # 2. Input prohibited HTML into the Description field
        # ---------------------------------------------------------------
        await page.fill(DESCRIPTION_SELECTOR, "<script>alert('x')</script>")

        # ---------------------------------------------------------------
        # 3. Attempt to save the form
        # ---------------------------------------------------------------
        await page.click(SAVE_BUTTON_SELECTOR)

        # ---------------------------------------------------------------
        # 4. Verify validation message is displayed
        # ---------------------------------------------------------------
        validation_locator = page.locator(f"text={VALIDATION_MESSAGE_TEXT}")
        await expect(validation_locator).to_be_visible()

        # ---------------------------------------------------------------
        # 5. Ensure the save operation was blocked (URL unchanged)
        # ---------------------------------------------------------------
        await expect(page).to_have_url(BASE_URL)

        # Clean‑up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
