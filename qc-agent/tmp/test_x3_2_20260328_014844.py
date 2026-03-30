import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these constants to match your application under test
BASE_URL = "http://localhost:3000/create-user"  # URL of the Create User form page
PASSWORD_INPUT_SELECTOR = "input[name=\"password\"]"
# Example selector for the eye‑icon toggle – replace with the actual selector used in your app
PASSWORD_TOGGLE_SELECTOR = "button[aria-label=\"Toggle password visibility\"]"

async def verify_password_visibility_toggle(page):
    # Locate the password input and the visibility toggle button
    password_input = page.locator(PASSWORD_INPUT_SELECTOR)
    toggle_button = page.locator(PASSWORD_TOGGLE_SELECTOR)

    # Ensure the password field is initially of type "password"
    await expect(password_input).to_have_attribute("type", "password")

    # Click the eye‑icon to make the password visible
    await toggle_button.click()
    # Verify the password characters become visible (type changes to "text")
    await expect(password_input).to_have_attribute("type", "text")

    # Click the eye‑icon again to mask the password
    await toggle_button.click()
    # Verify the password is masked again (type reverts to "password")
    await expect(password_input).to_have_attribute("type", "password")

async def main():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless mode can be toggled via the "headless" flag)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the Create User form page
        await page.goto(BASE_URL)

        # Perform the password visibility toggle verification
        await verify_password_visibility_toggle(page)

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
