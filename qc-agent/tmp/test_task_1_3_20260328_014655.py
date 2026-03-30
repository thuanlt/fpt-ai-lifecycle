import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SERVICE_CATALOG_URL = "https://your-application-domain.com/service-catalog"  # TODO: replace with actual URL

# Selectors – adjust according to the actual DOM structure of the Service Catalog page
PROCESS_STEPS_CONTAINER = "[data-test-id='process-steps']"          # Container element for the wizard steps
STEP_ITEM = "[data-test-id='process-step']"                       # Individual step element
ACTIVE_STEP_CLASS = "active"                                      # CSS class indicating the active step
STEP_NUMBER = ".step-number"                                      # Element inside a step that shows the number
STEP_TITLE = ".step-title"                                        # Element inside a step that shows the title

# Expected data – modify to reflect the real specification of the Service Catalog wizard
EXPECTED_STEPS = [
    {"number": "1", "title": "Request Details"},
    {"number": "2", "title": "Approval"},
    {"number": "3", "title": "Confirmation"},
]

# Breakpoint definition (in pixels) – typical value where layout switches from horizontal to vertical
HORIZONTAL_BREAKPOINT = 768

async def verify_process_steps(page, is_mobile: bool):
    """Verify the default state of the Process Steps component.

    Args:
        page: Playwright Page object already navigated to the Service Catalog screen.
        is_mobile: Boolean flag indicating whether the test is running in mobile viewport.
    """
    # Wait for the process steps container to be visible
    await page.wait_for_selector(PROCESS_STEPS_CONTAINER, state="visible")
    container = page.locator(PROCESS_STEPS_CONTAINER)

    # Verify orientation (horizontal for desktop, vertical for mobile)
    # We infer orientation by checking the computed CSS flex-direction property.
    flex_direction = await container.evaluate("el => getComputedStyle(el).flexDirection")
    expected_direction = "column" if is_mobile else "row"
    assert flex_direction == expected_direction, (
        f"Process steps orientation mismatch: expected '{expected_direction}' but got '{flex_direction}'."
    )

    # Locate all step items
    steps = container.locator(STEP_ITEM)
    step_count = await steps.count()
    assert step_count == len(EXPECTED_STEPS), (
        f"Number of steps mismatch: expected {len(EXPECTED_STEPS)} but found {step_count}."
    )

    # Iterate through each step and validate number, title and active state
    for index in range(step_count):
        step = steps.nth(index)
        # Verify step number
        number_el = step.locator(STEP_NUMBER)
        number_text = (await number_el.text_content()).strip()
        expected_number = EXPECTED_STEPS[index]["number"]
        assert number_text == expected_number, (
            f"Step {index + 1} number mismatch: expected '{expected_number}' but got '{number_text}'."
        )
        # Verify step title
        title_el = step.locator(STEP_TITLE)
        title_text = (await title_el.text_content()).strip()
        expected_title = EXPECTED_STEPS[index]["title"]
        assert title_text == expected_title, (
            f"Step {index + 1} title mismatch: expected '{expected_title}' but got '{title_text}'."
        )
        # Verify active/inactive state
        classes = await step.get_attribute("class")
        is_active = ACTIVE_STEP_CLASS in (classes or "")
        if index == 0:
            # First step must be active
            assert is_active, f"Step 1 should be active but is not. Classes: '{classes}'."
        else:
            # Subsequent steps must be inactive
            assert not is_active, f"Step {index + 1} should be inactive but is marked active. Classes: '{classes}'."

async def run_test():
    async with async_playwright() as p:
        # -------------------------------------------------------------------
        # Desktop scenario (horizontal layout)
        # -------------------------------------------------------------------
        browser = await p.chromium.launch(headless=False)  # Set headless=True for CI environments
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        await page.goto(SERVICE_CATALOG_URL)
        await verify_process_steps(page, is_mobile=False)
        await context.close()

        # -------------------------------------------------------------------
        # Mobile scenario (vertical layout)
        # -------------------------------------------------------------------
        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                         "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        )
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto(SERVICE_CATALOG_URL)
        await verify_process_steps(mobile_page, is_mobile=True)
        await mobile_context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
