import asyncio
import json
from playwright.async_api import async_playwright, Request, APIResponse

API_BASE_URL = "http://localhost"  # Adjust to your application's base URL
CREATE_USER_ENDPOINT = "/api/admin/users"

async def test_create_user_missing_email():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium) – required to obtain a request context
        browser = await p.chromium.launch()
        context = await browser.new_context()
        # Build the request payload without the required 'email' field
        payload = {
            "username": "testuser",
            "password": "P@ssw0rd!",
            # "email" is intentionally omitted to trigger validation error
        }
        # Send POST request
        response: APIResponse = await context.request.post(
            url=f"{API_BASE_URL}{CREATE_USER_ENDPOINT}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        # Verify HTTP status code is 400 Bad Request
        assert response.status == 400, f"Expected status 400, got {response.status}"
        # Parse response body (assuming JSON)
        try:
            body = await response.json()
        except Exception:
            body_text = await response.text()
            raise AssertionError(f"Response is not valid JSON. Body: {body_text}")
        # Verify error message mentions missing 'email' field
        error_message = body.get("error") or body.get("message") or ""
        assert "email" in error_message.lower(), (
            f"Expected error message to mention missing 'email' field, got: '{error_message}'"
        )
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_create_user_missing_email())
