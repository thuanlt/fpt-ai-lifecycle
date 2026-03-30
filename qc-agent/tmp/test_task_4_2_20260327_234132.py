import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Replace with the actual Login API endpoint
        url = "https://example.com/api/login"

        # Payload for a successful login with remember_me flag
        payload = {
            "username": "valid_user",
            "password": "valid_password",
            "remember_me": True
        }

        # Send POST request to the Login API
        response = await page.request.post(url, data=payload)

        # Assert status code 200
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse JSON response
        json_body = await response.json()

        # Assert token is present
        assert "token" in json_body, "Response missing 'token' field"

        # Assert expiry is present and is a future timestamp
        assert "expiry" in json_body, "Response missing 'expiry' field"
        import time
        expiry_ts = json_body["expiry"]
        # Assuming expiry is returned as epoch seconds
        assert expiry_ts > int(time.time()), "Token expiry is not in the future"

        print("Login API test passed successfully.")

        await browser.close()

asyncio.run(run())