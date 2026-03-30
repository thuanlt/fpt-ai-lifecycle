import asyncio
from playwright.async_api import async_playwright, expect

# Replace this with the actual URL of the application under test
APP_URL = "http://localhost:3000"

async def run_test():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the application page
        await page.goto(APP_URL)

        # ------------------------------------------------------------
        # Step 1: Click the "Có" button to trigger the additional input
        # ------------------------------------------------------------
        có_button = page.get_by_role("button", name="Có")
        await expect(có_button).to_be_visible()
        await có_button.click()

        # Verify that a text input field appears with the correct placeholder
        input_field = page.get_by_placeholder("Mô tả chi tiết vấn đề...")
        await expect(input_field).to_be_visible()

        # ------------------------------------------------------------
        # Step 2: Attempt to submit with an empty input field
        # ------------------------------------------------------------
        # Assuming there is a submit button with a recognizable label, e.g., "Gửi" or similar.
        submit_button = page.get_by_role("button", name="Gửi")
        # The button should be disabled when the input is empty
        await expect(submit_button).to_be_disabled()

        # Try to click it anyway (Playwright will raise if disabled, so we skip the click)
        # Instead, we directly check the validation message that should appear.
        validation_msg = page.locator("text=Vui lòng nhập mô tả vấn đề")
        await expect(validation_msg).to_be_visible()
        # Optionally, verify the validation message is styled in red (color check)
        # This is a simple CSS property check; adjust the selector if needed.
        color = await validation_msg.evaluate("el => getComputedStyle(el).color")
        # Common red color in browsers is rgb(255, 0, 0) – we just log it for reference.
        print(f"Validation message color: {color}")

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run_test())
