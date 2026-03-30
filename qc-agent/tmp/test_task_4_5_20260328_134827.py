import asyncio
from playwright.async_api import async_playwright, APIResponse

# Configuration – adjust these values to match the target environment
BASE_URL = "https://example.com"   # Replace with the actual API host
LOGIN_ENDPOINT = "/api/login"      # Replace with the actual login endpoint
USERNAME = "lockedUser"
WRONG_PASSWORD = "wrongPass"
EXPECTED_LOCK_MESSAGE = "Account locked"

async def main() -> None:
    async with async_playwright() as p:
        # Create a request context for API calls
        request = await p.request.new_context(base_url=BASE_URL)

        payload = {
            "username": USERNAME,
            "password": WRONG_PASSWORD,
        }

        # -----------------------------------------------------------------
        # Step 1‑5: Perform 5 consecutive failed login attempts
        # -----------------------------------------------------------------
        for attempt in range(1, 6):
            response: APIResponse = await request.post(LOGIN_ENDPOINT, data=payload)
            # Expected: HTTP 401 Unauthorized for each failed attempt
            assert response.status == 401, (
                f"Attempt {attempt}: Expected status 401, got {response.status}"
            )
            body = await response.json()
            print(f"Attempt {attempt} → Status: {response.status}, Body: {body}")

        # -----------------------------------------------------------------
        # Step 6: Verify account is locked after the 5th failure
        # -----------------------------------------------------------------
        response: APIResponse = await request.post(LOGIN_ENDPOINT, data=payload)
        # Expected: HTTP 423 Locked with a specific message
        assert response.status == 423, (
            f"Lockout check: Expected status 423, got {response.status}"
        )
        body = await response.json()
        # The API may return the message under different keys (e.g., "message" or "error")
        actual_message = body.get("message") or body.get("error") or ""
        assert EXPECTED_LOCK_MESSAGE in actual_message, (
            f"Lockout check: Expected message containing '{EXPECTED_LOCK_MESSAGE}', got '{actual_message}'"
        )
        print(f"Lockout verification → Status: {response.status}, Body: {body}")

        # Clean up the request context
        await request.dispose()

# Entry point for the async script
if __name__ == "__main__":
    asyncio.run(main())
