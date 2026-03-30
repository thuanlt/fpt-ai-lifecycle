import asyncio
from playwright.async_api import async_playwright

# Replace with the actual API endpoint and valid credentials
API_URL = "https://example.com/login"
VALID_USERNAME = "test_user"
VALID_PASSWORD = "Test@1234"

async def test_login_success():
    async with async_playwright() as p:
        # Use Chromium for the request context
        browser = await p.chromium.launch()
        context = await browser.new_context()
        # Perform the POST request to the login endpoint
        response = await context.request.post(
            API_URL,
            data={
                "username": VALID_USERNAME,
                "password": VALID_PASSWORD
            }
        )
        # Assert the HTTP status code is 200
        assert response.status == 200, f"Expected status 200, got {response.status}"
        # Parse the JSON body
        json_body = await response.json()
        # Assert that the response contains the required keys
        assert "token" in json_body, "Response JSON missing 'token' key"
        assert "expires_in" in json_body, "Response JSON missing 'expires_in' key"
        # Optionally, validate that the token is a non-empty string
        assert isinstance(json_body["token"], str) and json_body["token"], "Token is not a valid non-empty string"
        # And that expires_in is a positive integer
        assert isinstance(json_body["expires_in"], int) and json_body["expires_in"] > 0, "expires_in is not a positive integer"
        print("Login success test passed.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login_success())
