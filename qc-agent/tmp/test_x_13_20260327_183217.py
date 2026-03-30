import asyncio
from playwright.async_api import async_playwright

async def main():
    # Replace with the actual endpoint URL you want to test
    endpoint = "https://example.com/api/your-endpoint"

    async with async_playwright() as p:
        # Create a request context without any authentication headers
        request_context = await p.request.new_context()
        response = await request_context.get(endpoint)

        # Validate HTTP status code is 401 Unauthorized
        assert response.status == 401, f"Expected status 401, got {response.status}"

        # Validate the error message indicates missing credentials
        response_text = await response.text()
        assert "missing credentials" in response_text.lower(), (
            "Error message does not indicate missing credentials"
        )

        print("Test passed: Unauthorized request correctly rejected.")

if __name__ == "__main__":
    asyncio.run(main())
