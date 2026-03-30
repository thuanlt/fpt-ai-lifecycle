import asyncio
from playwright.async_api import async_playwright, expect
import re

BASE_URL = "https://example.com"  # Replace with the actual API host

async def main():
    async with async_playwright() as p:
        # Create a request context (no browser needed for pure API testing)
        request_context = await p.request.new_context()

        # ---------------------------------------------------------------------
        # Test Data – adjust according to the real API contract
        # ---------------------------------------------------------------------
        payload = {
            "cartItems": [
                {"productId": "prod-001", "quantity": 2},
                {"productId": "prod-002", "quantity": 1}
            ],
            "shippingAddress": {
                "street": "123 Main St",
                "city": "Hanoi",
                "postalCode": "100000",
                "country": "VN"
            },
            "paymentToken": "tok_test_visa_4242"
        }

        # ---------------------------------------------------------------------
        # 1. Send POST request to create an order
        # ---------------------------------------------------------------------
        response = await request_context.post(
            f"{BASE_URL}/api/orders",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # ---------------------------------------------------------------------
        # 2. Verify response status code
        # ---------------------------------------------------------------------
        assert response.status == 201, f"Expected status 201, got {response.status}"
        print("✅ Response status is 201 Created")

        # ---------------------------------------------------------------------
        # 3. Verify response body fields
        # ---------------------------------------------------------------------
        resp_json = await response.json()
        assert "orderId" in resp_json, "Response JSON missing 'orderId'"
        assert resp_json.get("status") == "Processing", f"Expected status 'Processing', got {resp_json.get('status')}"
        assert "estimatedDelivery" in resp_json, "Response JSON missing 'estimatedDelivery'"
        print("✅ Response body contains required fields: orderId, status='Processing', estimatedDelivery")

        # ---------------------------------------------------------------------
        # 4. Verify Location header points to the newly created order resource
        # ---------------------------------------------------------------------
        location_header = response.headers.get("location")
        assert location_header is not None, "Missing 'Location' header in response"
        pattern = r"^/api/orders/[^/]+$"
        assert re.match(pattern, location_header), f"Location header '{location_header}' does not match pattern '{pattern}'"
        print(f"✅ Location header is correct: {location_header}")

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
