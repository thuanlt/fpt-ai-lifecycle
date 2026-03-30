import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Create a request context
        request_context = await p.request.new_context()
        url = "https://example.com/api/auth/login"
        payload = {
            "email": "user@example.com",
            "password": "CorrectPass123"
        }
        response = await request_context.post(
            url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        # Assert status code
        assert response.status == 200, f"Expected status 200, got {response.status}"
        # Assert Content-Type header
        content_type = response.headers.get("content-type")
        assert content_type == "application/json", f"Expected Content-Type application/json, got {content_type}"
        # Parse JSON body
        body = await response.json()
        # Verify required fields
        for field in ["token", "userId", "expiresIn"]:
            assert field in body, f"Response body missing field '{field}'"
        print("API login contract validation passed.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
