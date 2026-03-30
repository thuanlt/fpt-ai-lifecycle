import asyncio
import json
from playwright.async_api import async_playwright

async def test_create_service():
    async with async_playwright() as p:
        request_context = await p.request.new_context()
        payload = {
            "name": "Test Service",
            "description": "Automated test service",
            "version": "1.0.0"
        }
        response = await request_context.post(
            "http://localhost:8000/api/services",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 201, f"Expected 201, got {response.status}"
        body = await response.json()
        assert "id" in body, "Response body missing 'id'"
        service_id = body["id"]
        # Verify service appears in GET list
        list_response = await request_context.get("http://localhost:8000/api/services")
        assert list_response.status == 200, f"Expected 200, got {list_response.status}"
        services = await list_response.json()
        assert any(s["id"] == service_id for s in services), "Created service not found in list"
        await request_context.dispose()

async def main():
    await test_create_service()

if __name__ == "__main__":
    asyncio.run(main())