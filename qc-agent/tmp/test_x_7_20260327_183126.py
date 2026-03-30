import asyncio
from playwright.async_api import async_playwright, expect

# Adjust these selectors to match the actual application under test
SETTINGS_TOGGLE_SELECTOR = "[data-test-id='theme-toggle']"  # The toggle button for dark mode
BODY_SELECTOR = "body"
TEXT_ELEMENT_SELECTOR = "[data-test-id='sample-text']"  # Any visible text element to verify color contrast

# Expected design‑system token names (used in CSS custom properties or class names)
EXPECTED_DARK_BACKGROUND_TOKEN = "darkBackground"
EXPECTED_ON_DARK_TOKEN = "onDark"

async def run_test():
    async with async_playwright() as p:
        # Launch browser (headless by default). Change to "chromium", "firefox", or "webkit" as needed.
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the application under test.
        # ------------------------------------------------------------
        await page.goto("https://your-app-url.example.com")

        # ------------------------------------------------------------
        # 2. Switch the theme to Dark mode via the Settings toggle.
        # ------------------------------------------------------------
        toggle = page.locator(SETTINGS_TOGGLE_SELECTOR)
        await expect(toggle).to_be_visible()
        await toggle.click()

        # ------------------------------------------------------------
        # 3. Verify that the background color of the page uses the darkBackground token.
        # ------------------------------------------------------------
        # The implementation may expose the token name via a CSS custom property,
        # a data attribute, or a class name. Below we check three common approaches.
        # Adjust the logic according to the actual app.
        # -----------------------------------------------------------------
        # a) Check for a CSS custom property on the <body> element.
        dark_bg_css = await page.evaluate(
            "element => getComputedStyle(element).getPropertyValue('--" + EXPECTED_DARK_BACKGROUND_TOKEN + "')",
            await page.query_selector(BODY_SELECTOR)
        )
        if dark_bg_css.strip():
            print(f"✅ Dark background token found via CSS variable: {dark_bg_css.strip()}")
        else:
            # b) Fallback – check for a class name that includes the token name.
            body_class = await page.evaluate(
                "element => element.className",
                await page.query_selector(BODY_SELECTOR)
            )
            if EXPECTED_DARK_BACKGROUND_TOKEN in body_class:
                print(f"✅ Dark background token present in body class: {body_class}")
            else:
                # c) Final fallback – check a data attribute.
                data_token = await page.evaluate(
                    f"element => element.getAttribute('data-token')",
                    await page.query_selector(BODY_SELECTOR)
                )
                if data_token == EXPECTED_DARK_BACKGROUND_TOKEN:
                    print("✅ Dark background token found via data-token attribute")
                else:
                    raise AssertionError("❌ Dark background token not applied after toggling dark mode")

        # ------------------------------------------------------------
        # 4. Verify that a sample text element uses the onDark token for its color.
        # ------------------------------------------------------------
        text_elem = page.locator(TEXT_ELEMENT_SELECTOR)
        await expect(text_elem).to_be_visible()

        # a) Check CSS custom property for text color.
        text_color_css = await page.evaluate(
            "element => getComputedStyle(element).getPropertyValue('--" + EXPECTED_ON_DARK_TOKEN + "')",
            await text_elem.element_handle()
        )
        if text_color_css.strip():
            print(f"✅ Text color token found via CSS variable: {text_color_css.strip()}")
        else:
            # b) Check computed color against a known value (if token maps to a hex/rgb).
            computed_color = await page.evaluate(
                "element => getComputedStyle(element).color",
                await text_elem.element_handle()
            )
            # Here you would compare `computed_color` to the expected value derived from the design system.
            # For demonstration, we simply log the value.
            print(f"ℹ️ Computed text color: {computed_color}")
            # Optionally raise if the color does not meet contrast requirements.
            # raise AssertionError("❌ Text color does not match onDark token after dark mode activation")

        # ------------------------------------------------------------
        # Clean up
        # ------------------------------------------------------------
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
