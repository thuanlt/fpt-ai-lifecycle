import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Test Case: Verify that optional description field can be left empty when
# creating a Service Instance.
# Steps:
#   1. Navigate to the Service Registry > Instance Management page.
#   2. Click the "Create Service Instance" button.
#   3. Fill all mandatory fields (e.g., Service Name, Version).
#   4. Leave the Description field blank.
#   5. Click "Save".
#   6. Verify the instance is created without errors and the Description column
#      is empty in the instance list.
# ---------------------------------------------------------------------------

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # 1. Navigate to the Service Registry / Instance Management page
        # ---------------------------------------------------------------
        # TODO: Replace with the actual URL of the application under test
        await page.goto("https://your-application-domain.com/service-registry/instances")

        # ---------------------------------------------------------------
        # 2. Click the "Create Service Instance" button
        # ---------------------------------------------------------------
        # TODO: Replace selector with the actual button locator
        await page.click("button#create-instance")

        # ---------------------------------------------------------------
        # 3. Fill mandatory fields
        # ---------------------------------------------------------------
        # Example mandatory fields – adjust selectors & values as needed
        await page.fill("input[name='serviceName']", "TestService")
        await page.fill("input[name='serviceVersion']", "1.0.0")
        # If there are other mandatory dropdowns or selectors, handle them here
        # e.g., await page.select_option("select[name='environment']", "prod")

        # ---------------------------------------------------------------
        # 4. Leave Description field empty (optional field)
        # ---------------------------------------------------------------
        # Ensure the description field is cleared (in case it has a default value)
        await page.fill("textarea[name='description']", "")

        # ---------------------------------------------------------------
        # 5. Click "Save" to create the instance
        # ---------------------------------------------------------------
        # TODO: Replace selector with the actual Save button locator
        await page.click("button#save-instance")

        # ---------------------------------------------------------------
        # 6. Verify instance creation succeeded and Description column is empty
        # ---------------------------------------------------------------
        # a) Wait for a success toast/notification (adjust selector/text as needed)
        try:
            success_toast = page.locator("div.toast-success")
            await expect(success_toast).to_be_visible(timeout=5000)
        except Exception as e:
            print("Success notification not found:", e)
            await browser.close()
            return

        # b) Locate the newly created row in the instances table
        # Assuming the table has a row with the service name we just entered
        row_locator = page.locator(f"//tr[td[text()='TestService'] and td[text()='1.0.0']]")
        await expect(row_locator).to_be_visible(timeout=5000)

        # c) Verify the Description column (assumed to be the third <td>) is empty
        description_cell = row_locator.locator("td:nth-child(3)")
        description_text = await description_cell.text_content()
        assert description_text is None or description_text.strip() == "", (
            f"Description column is not empty. Found: '{description_text}'"
        )

        print("Test passed: Optional description field can be left empty and instance is created correctly.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
