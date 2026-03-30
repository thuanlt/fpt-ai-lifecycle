import asyncio
import json
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Configuration – replace with the real endpoint and credentials for your app
# ---------------------------------------------------------------------------
LOGIN_URL = "https://example.com/api/login"
PAYLOAD = {
    "username": "test_user",
    "password": "test_password"
}
HEADERS = {
    "Content-Type": "application/json"
}

async def main() -> None:
    async with async_playwright() as p:
        # Create a request‑only context (no browser UI needed)
        request_context = await p.request.new_context()
        responses = []

        # ---------------------------------------------------------------
        # Send 20 rapid login attempts (no explicit delay – fire‑and‑forget)
        # ---------------------------------------------------------------
        for i in range(20):
            response = await request_context.post(
                LOGIN_URL,
                headers=HEADERS,
                data=json.dumps(PAYLOAD)
            )
            responses.append(response)

        # ---------------------------------------------------------------
        # Validate the first 10 responses – they may be successful (200) or
        # rejected due to bad credentials (401). Any other status is a failure.
        # ---------------------------------------------------------------
        for idx, resp in enumerate(responses[:10], start=1):
            if resp.status not in (200, 401):
                raise AssertionError(
                    f"Request {idx}: expected status 200 or 401, got {resp.status}"
                )

        # ---------------------------------------------------------------
        # Validate the remaining 10 responses – they must be rate‑limited (429).
        # ---------------------------------------------------------------
        for idx, resp in enumerate(responses[10:], start=11):
            if resp.status != 429:
                raise AssertionError(
                    f"Request {idx}: expected status 429, got {resp.status}"
                )

        print("✅ Rate limiting test passed.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
