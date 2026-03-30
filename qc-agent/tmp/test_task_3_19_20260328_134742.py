import asyncio
from playwright.async_api import async_playwright

# Configuration – replace with the actual base URL of the application under test
BASE_URL = "https://example.com"  # <-- update this to the real host
LOGIN_ENDPOINT = "/api/login"      # <-- update if the path differs
INVALID_CREDENTIALS = {
    "username": "invalid_user",
    "password": "invalid_pass"
}

async def run_rate_limit_test():
    async with async_playwright() as pw:
        # Create a request‑only context (no browser UI needed)
        request_context = await pw.request.new_context(base_url=BASE_URL)

        responses = []
        # Send 20 rapid POST requests with invalid credentials
        for i in range(20):
            response = await request_context.post(
                LOGIN_ENDPOINT,
                data=INVALID_CREDENTIALS,
                # Optional: set a very short timeout to keep the loop fast
                timeout=5000
            )
            responses.append(response)
            # Small pause can be omitted to keep the attempts "rapid"

        # Identify the first response that indicates rate limiting (HTTP 429)
        rate_limited_response = None
        for resp in responses:
            if resp.status == 429:
                rate_limited_response = resp
                break

        # Assertions – these will raise AssertionError if the expectations are not met
        assert rate_limited_response is not None, (
            "Rate limiting was not triggered after 20 rapid attempts."
        )
        assert "retry-after" in rate_limited_response.headers, (
            "Expected 'Retry-After' header is missing in the 429 response."
        )

        # Output useful information for the test run
        print(
            f"Rate limiting triggered: status={rate_limited_response.status}, "
            f"Retry-After={rate_limited_response.headers.get('retry-after')}"
        )

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(run_rate_limit_test())
