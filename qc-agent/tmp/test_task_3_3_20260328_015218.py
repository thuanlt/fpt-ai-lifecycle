import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:3000"  # <-- Replace with the actual application URL
CREATE_SERVICE_BUTTON_SELECTOR = "text=Create New Service"  # Button/link that opens the form
FORM_CONTAINER_SELECTOR = "form#service-form"            # Unique selector for the form
SAVE_BUTTON_SELECTOR = "button:has-text(\"Save\")"   # Save button inside the form
# Expected validation messages – adjust the text if the app uses different wording
VALIDATION_MESSAGES = [
    "Name is required",
    "Category is required",
    # Add other mandatory field messages here if needed
]

async def run_test():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # Step 1: Open the "Create New Service" form
        # ---------------------------------------------------------------
        await page.goto(BASE_URL)
        # Click the button/link that opens the form
        await page.click(CREATE_SERVICE_BUTTON_SELECTOR)
        # Verify that the form is displayed
        form = page.locator(FORM_CONTAINER_SELECTOR)
        await expect(form).to_be_visible()
        print("✅ Form is displayed")

        # ---------------------------------------------------------------
        # Step 2: Click the "Save" button without entering any data
        # ---------------------------------------------------------------
        await page.click(SAVE_BUTTON_SELECTOR)

        # ---------------------------------------------------------------
        # Step 3: Verify validation messages appear for each mandatory field
        # ---------------------------------------------------------------
        for msg in VALIDATION_MESSAGES:
            # Assuming each validation message appears as a visible text element
            validation_locator = page.locator(f"text={msg}")
            await expect(validation_locator).to_be_visible()
            print(f"✅ Validation message displayed: '{msg}'")

        # ---------------------------------------------------------------
        # Step 4: Verify the service is NOT saved and the form remains open
        # ---------------------------------------------------------------
        # The form should still be visible after the failed save attempt
        await expect(form).to_be_visible()
        print("✅ Form remains displayed, indicating the service was not saved")

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
