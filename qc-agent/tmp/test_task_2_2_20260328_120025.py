import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the Service Registry application
        await page.goto("http://localhost:3000")

        # Step 1: Click the "Create Instance" button to open the form
        await page.click('text="Create Instance"')

        # Verify that mandatory fields have an asterisk (*) next to their labels
        required_fields = ["Instance Name", "Service Type", "Version"]
        for field_name in required_fields:
            # Locate the label associated with the field
            label_locator = page.locator(f'label:has-text("{field_name}")')
            # Wait for the label to be visible
            await label_locator.wait_for(state="visible")
            # Retrieve the full label text
            label_text = await label_locator.inner_text()
            # Assertion: asterisk must be present in the label text
            assert "*" in label_text, (
                f"Mandatory asterisk not found for field '{field_name}'. "
                f"Label text received: '{label_text}'"
            )

        # Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
