import asyncio
from playwright.async_api import async_playwright, expect


async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI environments)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # ---------------------------------------------------------------------
        # Mock the authentication service to simulate an outage (HTTP 503).
        # Adjust the URL pattern to match the real login API endpoint used by the
        # application under test.
        # ---------------------------------------------------------------------
        async def route_handler(route, request):
            if "/api/auth/login" in request.url:
                await route.fulfill(
                    status=503,
                    content_type="application/json",
                    body='{"error":"Service unavailable"}'
                )
            else:
                await route.continue_()

        await context.route("**/*", route_handler)

        page = await context.new_page()
        # Replace with the actual login page URL
        await page.goto("https://example.com/login")

        # ---------------------------------------------------------------------
        # Fill in **valid** credentials – these values are arbitrary but must be
        # accepted by the front‑end validation logic before the request is sent.
        # ---------------------------------------------------------------------
        await page.fill('input[name="username"]', "validUser")
        await page.fill('input[name="password"]', "validPass")
        await page.click('button[type="submit"]')

        # ---------------------------------------------------------------------
        # Verify that the generic error message is shown and that no sensitive
        # information (e.g., the username) is leaked.
        # Adjust the selector to match the actual DOM element that displays the
        # error.
        # ---------------------------------------------------------------------
        error_locator = page.locator('.error-message')
        await expect(error_locator).to_be_visible()
        error_text = await error_locator.text_content()

        # Expected generic message
        assert "Service unavailable" in error_text, (
            f"Unexpected error message: {error_text}"
        )
        # Ensure no sensitive data is exposed
        assert "validUser" not in error_text, (
            "Sensitive information exposed in error message"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
