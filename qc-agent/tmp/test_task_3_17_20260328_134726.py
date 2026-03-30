import asyncio
from playwright.async_api import async_playwright
import json

async def test_login_api():
    async with async_playwright() as p:
        request_context = await p.request.new_context()
        payload = {"username": "user@example.com", "password": "CorrectPass123"}
        response = await request_context.post(
            "http://localhost/api/auth/login",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 200, f"Expected status 200, got {response.status}"
        resp_json = await response.json()
        assert "token" in resp_json, "Response does not contain 'token'"
        token = resp_json["token"]
        # Simple JWT format validation (header.payload.signature)
        assert isinstance(token, str) and token.count('.') == 2, "Token is not a valid JWT"
        print("Login API test passed. Token received.")

async def main():
    await test_login_api()

if __name__ == "__main__":
    asyncio.run(main())