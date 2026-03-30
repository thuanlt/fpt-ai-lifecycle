import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://example.com/api/login"
LOGIN_PAYLOAD = {"username": "user", "password": "pass"}

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        # Use Playwright's HTTP client for API calls
        http = await context.new_async_http_client()

        statuses = []
        responses = []

        for i in range(101):
            response = await http.post(BASE_URL, json=LOGIN_PAYLOAD)
            statuses.append(response.status)
            try:
                body = await response.json()
            except Exception:
                body = None
            responses.append(body)
            # Optional: small delay to avoid overwhelming the server
            await asyncio.sleep(0.05)

        await http.dispose()
        await context.close()
        await browser.close()

        # Assert that the 100th request (index 99) returns 429
        assert statuses[99] == 429, f"Expected 429 on 100th request, got {statuses[99]}"
        # Assert that the response body contains the expected error message
        error_msg = "rate limit exceeded"
        assert responses[99] is not None, "Response body is None"
        assert error_msg in str(responses[99]), f"Expected error message '{error_msg}' not found in response"
        print("Test passed: Rate limiting works as expected.")

if __name__ == "__main__":
    asyncio.run(run_test())