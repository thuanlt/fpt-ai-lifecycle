import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:3000"  # adjust as needed

async def main():
    async with async_playwright() as p:
        request_context = await p.request.new_context(base_url=BASE_URL)

        payload = {
            "productId": "12345",
            "quantity": 1
        }

        response = await request_context.post("/api/cart/add", data=payload)

        # Assert status code
        assert response.status == 200, f"Expected status 200, got {response.status}"

        json_body = await response.json()

        # Validate response contains updated cart summary with new item count
        assert "cartSummary" in json_body, "Response missing 'cartSummary'"
        assert "itemCount" in json_body["cartSummary"], "Cart summary missing 'itemCount'"
        assert json_body["cartSummary"]["itemCount"] >= 1, "Item count should be at least 1"

        # Validate server returns current cart version/token for concurrency control
        assert "cartVersionToken" in json_body, "Response missing 'cartVersionToken'"
        assert isinstance(json_body["cartVersionToken"], str) and json_body["cartVersionToken"], "Invalid cartVersionToken"

        print("Add-to-cart API test passed.")

        await request_context.dispose()

asyncio.run(main())
