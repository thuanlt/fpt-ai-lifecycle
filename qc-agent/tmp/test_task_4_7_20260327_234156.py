import asyncio
from playwright.async_api import async_playwright

# Configuration
BASE_URL = "https://example.com/api"
LOGIN_ENDPOINT = "/login"
PROTECTED_ENDPOINT = "/protected"
USERNAME = "testuser"
PASSWORD = "testpass"
BUFFER_SECONDS = 5

async def run():
    async with async_playwright() as p:
        # Launch browser and create a new context
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # 1. Send POST /login with valid credentials
        login_response = await request.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            data={"username": USERNAME, "password": PASSWORD}
        )
        assert login_response.status == 200, f"Expected 200, got {login_response.status}"
        login_json = await login_response.json()
        token = login_json.get("token")
        expires_in = login_json.get("expires_in")
        assert token is not None, "Token missing in response"
        assert isinstance(expires_in, int), "expires_in missing or not an integer"
        print(f"Token received: {token}, expires_in: {expires_in}s")

        # 2. Wait until expires_in + buffer
        await asyncio.sleep(expires_in + BUFFER_SECONDS)

        # 3. Use token to access protected endpoint
        protected_response = await request.get(
            f"{BASE_URL}{PROTECTED_ENDPOINT}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status == 401, f"Expected 401, got {protected_response.status}"
        print("Protected endpoint returned 401 as expected after token expiration.")

        # Clean up
        await context.close()
        await browser.close()

asyncio.run(run())