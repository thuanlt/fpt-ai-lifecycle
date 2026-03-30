import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://example.com/api"  # Replace with actual base URL
LOGIN_ENDPOINT = f"{BASE_URL}/login"
PROTECTED_ENDPOINT = f"{BASE_URL}/protected"

async def main():
    async with async_playwright() as p:
        # Create a new request context
        context = await p.chromium.launch()
        # 1. Login to get token
        login_payload = {
            "username": "test_user",
            "password": "test_password"
        }
        login_response = await context.request.post(LOGIN_ENDPOINT, data=login_payload)
        assert login_response.status == 200, f"Expected 200, got {login_response.status}"
        login_json = await login_response.json()
        token = login_json.get("token")
        assert token, "Token not found in login response"

        # 2. Call /protected with Authorization header Bearer token
        protected_response = await context.request.get(
            PROTECTED_ENDPOINT,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status == 200, f"Expected 200, got {protected_response.status}"
        print("Test passed: Protected resource accessed successfully.")

        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
