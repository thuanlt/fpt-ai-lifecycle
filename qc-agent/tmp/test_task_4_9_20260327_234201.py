import asyncio
from playwright.async_api import async_playwright

# Replace with the actual base URL of the API
BASE_URL = "https://api.example.com"

async def main():
    async with async_playwright() as p:
        # Create a new request context (no cookies, no auth headers)
        client = await p.request.new_context()

        # Attempt to access a protected resource without an Authorization header
        response = await client.get(f"{BASE_URL}/protected")

        # Assert that the response status code is 401 Unauthorized
        assert response.status == 401, f"Expected 401, got {response.status}"
        print("Test passed: Received 401 Unauthorized as expected.")

if __name__ == "__main__":
    asyncio.run(main())