import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://your-api-domain.com"  # Replace with the actual API base URL
PRODUCT_ID = "98765"

async def main():
    async with async_playwright() as p:
        # Create a request context (no browser needed for pure API testing)
        request_context = await p.request.new_context()
        
        # Send GET request for the product details
        response = await request_context.get(f"{BASE_URL}/api/products/{PRODUCT_ID}")
        
        # Verify response status
        assert response.status == 200, f"Expected status 200, got {response.status}"
        
        # Parse JSON body
        json_body = await response.json()
        
        # Required fields to validate
        required_fields = [
            "id",
            "name",
            "description",
            "price",
            "images",
            "specifications",
            "reviews",
            "stockAvailability",
        ]
        
        # Check each required field exists in the response
        for field in required_fields:
            assert field in json_body, f"Missing field '{field}' in response"
        
        # Additional optional checks (e.g., ensure arrays are indeed lists)
        assert isinstance(json_body.get("images", []), list), "'images' should be a list"
        assert isinstance(json_body.get("reviews", []), list), "'reviews' should be a list"
        
        print("✅ Product detail retrieval test passed.")
        
        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
