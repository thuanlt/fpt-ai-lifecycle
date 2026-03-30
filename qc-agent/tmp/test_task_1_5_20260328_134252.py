import asyncio
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Configuration – replace with the actual URL of the login page you want to test
# ---------------------------------------------------------------------------
LOGIN_PAGE_URL = "https://example.com/login"  # <-- Update this URL

# Viewport size for tablet verification (width x height)
TABLET_VIEWPORT = {"width": 768, "height": 1024}

# Acceptable tolerance (in pixels) when checking centering alignment
CENTER_TOLERANCE_PX = 5

async def verify_centered(element_bbox, viewport_width, element_name: str):
    """Verify that an element is horizontally centered within the given tolerance.

    Args:
        element_bbox (dict): Bounding box dict returned by ``element.bounding_box()``.
        viewport_width (int): Width of the viewport.
        element_name (str): Human‑readable name for logging.
    """
    element_x = element_bbox["x"]
    element_width = element_bbox["width"]
    expected_x = (viewport_width - element_width) / 2
    diff = abs(element_x - expected_x)
    if diff <= CENTER_TOLERANCE_PX:
        print(f"✅ {element_name} is centered (diff={diff:.2f}px ≤ {CENTER_TOLERANCE_PX}px)")
    else:
        raise AssertionError(
            f"{element_name} is not centered: expected x≈{expected_x:.2f}, got {element_x:.2f} (diff={diff:.2f}px)"
        )

async def main():
    async with async_playwright() as p:
        # Launch a Chromium browser (headless can be set to False for debugging)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport=TABLET_VIEWPORT)
        page = await context.new_page()

        # ---------------------------------------------------------------
        # Step 1 – Navigate to the login page
        # ---------------------------------------------------------------
        await page.goto(LOGIN_PAGE_URL)
        print(f"Navigated to {LOGIN_PAGE_URL} with viewport {TABLET_VIEWPORT['width']}x{TABLET_VIEWPORT['height']}")

        # ---------------------------------------------------------------
        # Step 2 – Locate the input fields and login button
        # ---------------------------------------------------------------
        # Adjust selectors according to the actual DOM of the login page.
        username_input = page.locator("input[name='username'], input#username, input[type='email']")
        password_input = page.locator("input[name='password'], input#password, input[type='password']")
        login_button = page.locator("button[type='submit'], button#login, button[name='login']")

        # Ensure the elements are visible before proceeding
        await username_input.wait_for(state="visible")
        await password_input.wait_for(state="visible")
        await login_button.wait_for(state="visible")

        # ---------------------------------------------------------------
        # Step 3 – Verify horizontal centering of each element
        # ---------------------------------------------------------------
        viewport_width = TABLET_VIEWPORT["width"]
        await verify_centered(await username_input.bounding_box(), viewport_width, "Username input")
        await verify_centered(await password_input.bounding_box(), viewport_width, "Password input")
        await verify_centered(await login_button.bounding_box(), viewport_width, "Login button")

        # ---------------------------------------------------------------
        # Step 4 – Verify vertical ordering (button below inputs)
        # ---------------------------------------------------------------
        username_bbox = await username_input.bounding_box()
        password_bbox = await password_input.bounding_box()
        button_bbox = await login_button.bounding_box()

        # The login button's top edge should be greater than the bottom edge of the password field
        if button_bbox["y"] > password_bbox["y"] + password_bbox["height"]:
            print("✅ Login button is positioned below the password input field")
        else:
            raise AssertionError(
                f"Login button is not below the password field: button y={button_bbox['y']}, "
                f"password bottom={password_bbox['y'] + password_bbox['height']}"
            )

        # ---------------------------------------------------------------
        # Cleanup
        # ---------------------------------------------------------------
        await context.close()
        await browser.close()
        print("Test completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
