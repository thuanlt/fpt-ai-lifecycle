import asyncio
from playwright.async_api import async_playwright, expect

# Replace this with the actual base URL of the application under test
BASE_URL = "https://example.com"

async def test_search_api_response_structure():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium). Browser UI is not needed for API testing,
        # but Playwright requires a browser context to create a request object.
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request = context.request

        # Send GET request to the product search endpoint with query parameter "espresso"
        endpoint = f"{BASE_URL}/api/products?search=espresso"
        response = await request.get(endpoint)

        # Assert HTTP status code 200 OK
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Parse JSON response body
        json_body = await response.json()

        # The response should be a JSON object containing at least two keys:
        #   - "totalCount": integer indicating total matching items
        #   - "products" (or the root array) containing product objects
        # Adjust the validation according to the actual API contract.
        # Here we assume the root is an object with "totalCount" and "items" array.
        # If the API returns a plain array, comment out the totalCount check.
        if isinstance(json_body, dict):
            # Validate totalCount field exists and is an integer
            assert "totalCount" in json_body, "Response missing 'totalCount' field"
            assert isinstance(json_body["totalCount"], int), "'totalCount' should be an integer"
            items = json_body.get("items") or json_body.get("products") or []
        elif isinstance(json_body, list):
            # If the response is a plain array, treat it as the items list
            items = json_body
        else:
            raise AssertionError("Unexpected JSON response format")

        # Ensure items is a list
        assert isinstance(items, list), "Products collection should be a list"

        # Validate each product object contains required fields
        required_fields = {"id", "name", "price", "imageUrl", "availability"}
        for idx, product in enumerate(items):
            assert isinstance(product, dict), f"Product at index {idx} is not an object"
            missing = required_fields - product.keys()
            assert not missing, f"Product at index {idx} missing fields: {missing}"

        # Clean up
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search_api_response_structure())
