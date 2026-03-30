import asyncio
from playwright.async_api import async_playwright, Request, APIResponse

BASE_URL = "http://localhost:3000"  # Adjust to the actual host and port of the application

async def test_get_services():
    async with async_playwright() as p:
        # Create a new API request context
        request_context = await p.request.new_context(base_url=BASE_URL)
        
        # Send GET request to /api/services
        response: APIResponse = await request_context.get("/api/services")
        
        # Verify response status code
        assert response.status == 200, f"Expected status 200, got {response.status}"
        
        # Parse JSON body
        json_body = await response.json()
        
        # Verify the body is a list/array
        assert isinstance(json_body, list), f"Expected response body to be a list, got {type(json_body)}"
        
        # Verify each service object contains required fields
        required_fields = {"id", "name", "version", "status"}
        for index, service in enumerate(json_body):
            assert isinstance(service, dict), f"Service at index {index} is not an object"
            missing = required_fields - service.keys()
            assert not missing, f"Service at index {index} is missing fields: {missing}"
        
        print("GET /api/services test passed.")
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(test_get_services())
