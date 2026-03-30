import asyncio
from playwright.async_api import async_playwright

# Base URL of the application under test. Adjust as needed.
BASE_URL = "http://localhost:8000"

async def main():
    async with async_playwright() as p:
        # Create a request context (no UI needed for API testing)
        request_context = await p.request.new_context()
        
        # Send DELETE request to a non‑existent user ID
        endpoint = f"{BASE_URL}/api/admin/users/999999"
        response = await request_context.delete(endpoint)
        
        # Verify HTTP status code is 404
        assert response.status == 404, f"Expected status 404, got {response.status}"
        
        # Verify response body contains the expected error message
        # Try to read as JSON first; fallback to plain text
        try:
            body = await response.json()
            # If the body is a dict, look for a key that may hold the message
            message = body.get("message", "") if isinstance(body, dict) else str(body)
        except Exception:
            message = await response.text()
        
        assert "User not found" in message, "Expected error message 'User not found' not found in response"
        
        print("[PASS] Delete non‑existent user returned 404 with correct error message.")
        
        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
