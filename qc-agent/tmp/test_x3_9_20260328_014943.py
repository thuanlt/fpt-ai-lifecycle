import asyncio
from playwright.async_api import async_playwright, expect

async def test_create_user_api():
    async with async_playwright() as p:
        # Launch a headless browser (required to obtain a request context)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        # Create a request session using the browser context
        request = await context.request

        # Define the payload for creating a new user
        payload = {
            "username": "testuser123",
            "email": "testuser123@example.com",
            "password": "SecureP@ssw0rd!",
            "role": "admin"
        }

        # Send POST request to the Create User API endpoint
        response = await request.post(
            url="http://localhost/api/admin/users",  # Adjust base URL as needed
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        # Assert that the response status code is 201 Created
        assert response.status == 201, f"Expected status 201, got {response.status}"

        # Parse JSON response body
        json_body = await response.json()

        # Verify that a userId is returned and that the echoed data matches the request
        assert "userId" in json_body, "Response body does not contain 'userId'"
        assert json_body.get("username") == payload["username"], "Username mismatch in response"
        assert json_body.get("email") == payload["email"], "Email mismatch in response"
        assert json_body.get("role") == payload["role"], "Role mismatch in response"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_create_user_api())
