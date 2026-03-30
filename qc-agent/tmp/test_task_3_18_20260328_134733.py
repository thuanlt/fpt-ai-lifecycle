import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Create a request context (adjust base_url as needed for your environment)
        request_context = await p.request.new_context(base_url="http://localhost")
        
        # Send POST request with invalid credentials
        response = await request_context.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpass"
            }
        )
        
        # Verify HTTP status code 401
        assert response.status == 401, f"Expected status 401, got {response.status}"
        
        # Verify response body contains the expected error message
        json_body = await response.json()
        assert "error" in json_body, "Response JSON does not contain 'error' field"
        expected_message = "Invalid username or password"
        actual_message = json_body["error"]
        assert actual_message == expected_message, (
            f"Expected error message '{expected_message}', got '{actual_message}'"
        )
        
        print("Test passed: Invalid credentials returned 401 with correct error message")
        await request_context.dispose()

asyncio.run(run())
