import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – replace with the actual URL of the login page under test.
# ---------------------------------------------------------------------------
LOGIN_URL = "https://your-application-domain.com/login"

# Selectors for the login page elements. Adjust if your application uses different
# attributes or element structures.
SELECTORS = {
    "username": "input[name='username']",
    "password": "input[name='password']",
    "remember_me": "input[name='remember']",
    "login_button": "button[type='submit']",
    "forgot_password": "a.forgot-password"
}

# Expected ARIA labels (or accessible names) for each control.
EXPECTED_LABELS = {
    "username": "Username",
    "password": "Password",
    "remember_me": "Remember Me",
    "login_button": "Log In",
    "forgot_password": "Forgot Password"
}

# Expected focus order when navigating with the Tab key.
EXPECTED_FOCUS_ORDER = [
    "username",
    "password",
    "remember_me",
    "login_button",
    "forgot_password"
]

async def verify_aria_labels(page):
    """Validate that each interactive element has the correct accessible name."""
    for key, selector in SELECTORS.items():
        element = await page.query_selector(selector)
        if not element:
            raise AssertionError(f"Element '{key}' not found using selector '{selector}'.")
        # Retrieve the accessibility snapshot for the element.
        snapshot = await page.accessibility.snapshot(root=element)
        # The accessible name is stored under the 'name' property.
        actual_name = snapshot.get("name", "").strip()
        expected_name = EXPECTED_LABELS[key]
        if actual_name != expected_name:
            raise AssertionError(
                f"ARIA label mismatch for '{key}': expected '{expected_name}', got '{actual_name}'."
            )
    print("✅ All ARIA labels are correct.")

async def get_active_element_selector(page):
    """Return a CSS selector that uniquely identifies the currently focused element."""
    # Evaluate in the browser context to obtain attributes of document.activeElement.
    return await page.evaluate(
        """
        () => {
            const el = document.activeElement;
            if (!el) return null;
            // Prefer id, then name, then a generic selector based on tag and type.
            if (el.id) return `#${el.id}`;
            if (el.name) return `[name='${el.name}']`;
            if (el.tagName.toLowerCase() === 'input' && el.type) {
                return `input[type='${el.type}']`;
            }
            return el.tagName.toLowerCase();
        }
        """
    )

async def verify_focus_order(page):
    """Navigate through the page using the Tab key and confirm the focus sequence."""
    # Ensure the page starts with no element focused (body).
    await page.evaluate("document.body.focus()")
    for index, key in enumerate(EXPECTED_FOCUS_ORDER):
        # Press Tab to move focus to the next element.
        await page.keyboard.press("Tab")
        # Small pause to allow focus change.
        await page.wait_for_timeout(100)
        active_selector = await get_active_element_selector(page)
        expected_selector = SELECTORS[key]
        # Resolve the expected selector to a concrete element for comparison.
        expected_element = await page.query_selector(expected_selector)
        if not expected_element:
            raise AssertionError(f"Expected element '{key}' not found using selector '{expected_selector}'.")
        # Compare the active element with the expected one.
        is_match = await page.evaluate(
            "(active, expected) => active.isSameNode(expected)",
            await page.evaluate_handle("document.activeElement"),
            expected_element
        )
        if not is_match:
            raise AssertionError(
                f"Focus order mismatch at position {index + 1}: expected '{key}' but focus is on element matching '{active_selector}'."
            )
    print("✅ Focus order via Tab navigation is correct.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for CI environments
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(LOGIN_URL)

        # Step 1: Verify ARIA labels / accessibility attributes.
        await verify_aria_labels(page)

        # Step 2: Verify focus order using keyboard Tab navigation.
        await verify_focus_order(page)

        # Clean up.
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
