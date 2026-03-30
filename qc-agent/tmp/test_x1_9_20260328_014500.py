import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless can be set to True for CI)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # TODO: Replace with the actual application URL
        await page.goto("https://your-application-url.com")

        # ---------- Step 1: Enter an excessively long search query ----------
        # Adjust the selector to match the real search input element
        search_input_selector = "input[name='q']"  # example selector
        await page.wait_for_selector(search_input_selector)
        long_query = "a" * 256  # 256‑character string
        await page.fill(search_input_selector, long_query)

        # ---------- Step 2: Submit the search ----------
        # Adjust the selector to match the real submit button
        submit_button_selector = "button[type='submit']"  # example selector
        await page.click(submit_button_selector)
        # Wait for navigation / network activity to settle
        await page.wait_for_load_state("networkidle")

        # ---------- Expected Result 1: Query is truncated to allowed limit (e.g., 128 chars) ----------
        # Verify the value present in the search box after submission
        truncated_value = await page.eval_on_selector(search_input_selector, "el => el.value")
        assert len(truncated_value) <= 128, (
            f"Search query was not truncated. Length observed: {len(truncated_value)}"
        )

        # ---------- Expected Result 2 (optional): Informational message is shown ----------
        info_message_selector = ".info-message"  # example selector for the truncation notice
        info_element = await page.query_selector(info_message_selector)
        if info_element:
            message_text = await info_element.inner_text()
            assert "Search term truncated to 128 characters" in message_text, (
                f"Expected truncation message not found. Got: '{message_text}'"
            )

        await browser.close()

asyncio.run(run())
