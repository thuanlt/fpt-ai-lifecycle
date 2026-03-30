import asyncio
import time
import jwt
from playwright.async_api import async_playwright

async def test_login_token():
    # Replace with the actual API endpoint and valid credentials
    api_url = "https://api.example.com/login"
    username = "valid_user"
    password = "valid_password"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Perform the login request
        response = await page.request.post(
            api_url,
            data={"username": username, "password": password}
        )

        # Assert status code 200
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse JSON response
        body = await response.json()
        token = body.get("token") or body.get("access_token")
        assert token, "Response does not contain a token"

        # Decode JWT without verifying signature (for test purposes)
        decoded = jwt.decode(token, options={"verify_signature": False})

        # Verify claims
        assert decoded.get("sub") == username, f"Expected sub claim '{username}', got '{decoded.get('sub')}'"
        exp_timestamp = decoded.get("exp")
        assert exp_timestamp is not None, "Token does not contain 'exp' claim"
        assert exp_timestamp > int(time.time()), "Token 'exp' claim is not in the future"

        print("Login token test passed.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login_token())