import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the support‑chat page (replace with actual URL)
        await page.goto("https://your-app-url.com/support-chat")

        # ---------------------------------------------------------------------
        # Verify apology message text
        # ---------------------------------------------------------------------
        apology_text = (
            "Xin lỗi vì sự cố này. Tôi sẽ cố gắng tìm hiểu thêm về vấn đề này và "
            "cung cấp thông tin hữu ích cho bạn. Tuy nhiên, tôi cần biết thông tin gì "
            "để giúp bạn tốt hơn. Bạn có muốn chia sẻ thêm về vấn đề của mình không?"
        )
        # Wait until the exact text appears on the page
        await page.wait_for_selector(f"text={apology_text}")
        assert await page.is_visible(f"text={apology_text}"), "Apology message is not visible"

        # ---------------------------------------------------------------------
        # Verify prompt text (question) – it is part of the same paragraph but we
        # check it explicitly to satisfy the test case description.
        # ---------------------------------------------------------------------
        prompt_text = "Bạn có muốn chia sẻ thêm về vấn đề của mình không?"
        await page.wait_for_selector(f"text={prompt_text}")
        assert await page.is_visible(f"text={prompt_text}"), "Prompt question is not visible"

        # ---------------------------------------------------------------------
        # Verify presence of response buttons "Có" and "Không"
        # ---------------------------------------------------------------------
        btn_yes = page.locator("button", has_text="Có")
        btn_no = page.locator("button", has_text="Không")

        await btn_yes.wait_for(state="visible")
        await btn_no.wait_for(state="visible")
        assert await btn_yes.is_visible(), "Button 'Có' is not visible"
        assert await btn_no.is_visible(), "Button 'Không' is not visible"

        # (Optional) Verify that both buttons are clickable
        await btn_yes.click()
        await btn_no.click()

        # Clean up
        await browser.close()

asyncio.run(run())
