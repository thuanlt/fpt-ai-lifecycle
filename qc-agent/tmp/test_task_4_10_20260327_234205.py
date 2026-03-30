import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Create a new request context
        client = await p.request.new_context()
        # Define the endpoint and headers
        url = "https://api.example.com/protected"  # Replace with actual API endpoint
        headers = {
            "Authorization": "Bearer invalidtoken"
        }
        # Send POST request (or GET if appropriate)
        response = await client.post(url, headers=headers)
        # Assert the response status code
        assert response.status == 401, f"Expected status 401, got {response.status}"
        print("Test passed: Received 401 Unauthorized")

asyncio.run(run())