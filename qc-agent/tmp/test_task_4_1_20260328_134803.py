import asyncio
import re
from playwright.async_api import async_playwright, Request, APIResponse

JWT_REGEX = re.compile(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$')

async def test_successful_login():
    async with async_playwright() as p:
        # Create a request context (no browser needed for API testing)
        request_context = await p.request.new_context()
        
        # Define the payload
        payload = {
            "username": "validUser",
            "password": "ValidPass123"
        }
        
        # Send POST request to the login endpoint
        response: APIResponse = await request_context.post(
            url="http://localhost/api/login",  # Adjust base URL as needed
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Assert HTTP 200 status
        assert response.status == 200, f"Expected status 200, got {response.status}"
        
        # Parse JSON response
        json_body = await response.json()
        
        # Verify that an authentication token is present
        assert "token" in json_body, "Response JSON does not contain 'token' field"
        token = json_body["token"]
        
        # Validate JWT format
        assert JWT_REGEX.match(token), f"Token does not match JWT format: {token}"
        
        print("✅ Successful login test passed.")
        
        # Clean up
        await request_context.dispose()

async def main():
    await test_successful_login()

if __name__ == "__main__":
    asyncio.run(main())
