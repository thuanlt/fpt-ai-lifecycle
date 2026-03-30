import asyncio
from playwright.async_api import async_playwright, Request, APIResponse

# Configuration
BASE_URL = "http://localhost"  # Adjust to your API host
LOGIN_ENDPOINT = "/api/login"
MALFORMED_JSON = "{\"username\": \"testuser\", \"password\": "  # Truncated JSON -> malformed
EXPECTED_STATUS = 500
EXPECTED_ERROR_SUBSTRING = "error"  # Generic error message substring to look for

async def test_malformed_login_payload():
    async with async_playwright() as p:
        # Create a request context (no UI needed)
        request_context = await p.request.new_context(base_url=BASE_URL)
        
        # Send POST request with malformed JSON body
        response: APIResponse = await request_context.post(
            LOGIN_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=MALFORMED_JSON  # raw string, not valid JSON
        )
        
        # Validate HTTP status code
        assert response.status == EXPECTED_STATUS, (
            f"Expected status {EXPECTED_STATUS}, got {response.status}"
        )
        
        # Validate response body contains a generic error message
        body_text = await response.text()
        assert EXPECTED_ERROR_SUBSTRING.lower() in body_text.lower(), (
            f"Response body does not contain expected error substring. Body: {body_text}"
        )
        
        print("✅ Malformed login payload test passed.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(test_malformed_login_payload())
