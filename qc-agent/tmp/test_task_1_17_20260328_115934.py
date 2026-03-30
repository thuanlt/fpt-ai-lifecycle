import asyncio
from playwright.async_api import async_playwright

async def test_duplicate_service_version():
    async with async_playwright() as p:
        # Create a request context (adjust base_url to your environment)
        request_context = await p.request.new_context(base_url="http://localhost:8000")
        
        # Ensure a service exists with a given name and version
        original_payload = {
            "name": "TestService",
            "version": "1.0.0",
            "description": "Initial version"
        }
        # Create the original service (ignore response – assume success)
        await request_context.post("/api/services", data=original_payload)
        
        # Attempt to create a duplicate version for the same service
        duplicate_payload = {
            "name": "TestService",
            "version": "1.0.0",
            "description": "Duplicate version attempt"
        }
        response = await request_context.post("/api/services", data=duplicate_payload)
        
        # Verify that the API returns 400 Bad Request
        assert response.status == 400, f"Expected status 400, got {response.status}"
        
        # Verify the error message in the response body
        json_body = await response.json()
        expected_message = "Version already exists for this service"
        actual_message = json_body.get("error") or json_body.get("message")
        assert actual_message == expected_message, (
            f"Expected error message '{expected_message}', got '{actual_message}'"
        )
        
        print("Test passed: duplicate version returns 400 with correct error message")
        await request_context.dispose()

asyncio.run(test_duplicate_service_version())
