import asyncio
from playwright.async_api import async_playwright

async def test_password_field():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        # Set a standard desktop viewport
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        # TODO: Replace with the actual login page URL
        await page.goto("https://example.com/login")

        # Selector for the password input field (type="password")
        password_selector = "input[type='password']"

        # 1. Verify password input field is visible
        await page.wait_for_selector(password_selector, state="visible")
        assert await page.is_visible(password_selector), "Password input field should be visible"

        # 2. Verify placeholder text reads "Password"
        placeholder = await page.get_attribute(password_selector, "placeholder")
        assert placeholder == "Password", f"Expected placeholder 'Password', got '{placeholder}'"

        # 3. Verify the input field is empty by default
        value = await page.input_value(password_selector)
        assert value == "", f"Expected empty input, got '{value}'"

        # 4. Verify the input type is password (masked)
        input_type = await page.get_attribute(password_selector, "type")
        assert input_type == "password", f"Expected type 'password', got '{input_type}'"

        await browser.close()

asyncio.run(test_password_field())
