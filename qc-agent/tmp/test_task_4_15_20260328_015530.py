import asyncio
from playwright.async_api import async_playwright, expect

# Replace this with a valid authentication token for the Service Catalog API
AUTH_TOKEN = "YOUR_VALID_TOKEN_HERE"

async def test_get_services_filtered_by_category():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium) – required to obtain a request context
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # Prepare the API request headers with the bearer token
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Accept": "application/json",
        }

        # Perform the GET request to the filtered endpoint
        response = await context.request.get(
            url="https://api.example.com/services?category=IT",
            headers=headers,
        )

        # Assert that the response status code is 200 OK
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse the JSON payload
        json_body = await response.json()

        # The API is expected to return a list (or an object containing a list) of services.
        # Adjust the extraction logic if the actual response shape differs.
        services = json_body if isinstance(json_body, list) else json_body.get("services", [])

        # Verify that each returned service has the category "IT"
        for idx, service in enumerate(services):
            category = service.get("category")
            assert (
                category == "IT"
            ), f"Service at index {idx} has unexpected category: {category}"

        # Clean up
        await context.close()
        await browser.close()

# Entry point for running the script directly
if __name__ == "__main__":
    asyncio.run(test_get_services_filtered_by_category())
