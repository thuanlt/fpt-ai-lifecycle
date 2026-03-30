import asyncio
from playwright.async_api import async_playwright

async def run():
    # Adjust the base URL to point to the environment under test
    base_url = "http://localhost:3000"  # <-- replace with actual host if different

    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(base_url=base_url)

        # NOTE: The service ID below must correspond to a service that has active
        # dependencies (e.g., linked incidents). Replace with a valid ID before
        # executing the script.
        service_id = "YOUR_SERVICE_ID_WITH_ACTIVE_DEPENDENCIES"

        # Perform the DELETE request
        response = await request_context.delete(f"/api/services/{service_id}")

        # Verify HTTP status code is 409 Conflict
        assert response.status == 409, f"Expected status 409, got {response.status}"

        # Verify the error message in the response body
        expected_message = "Cannot delete service with active dependencies"
        try:
            # Try to parse JSON response first
            body = await response.json()
            # Common keys that may hold the error message
            actual_message = (
                body.get("error")
                or body.get("message")
                or body.get("detail")
                or ""
            )
        except Exception:
            # Fallback to raw text if response is not JSON
            actual_message = await response.text()

        assert expected_message in actual_message, (
            f"Expected error message '{expected_message}' not found in response. "
            f"Actual message: '{actual_message}'"
        )

        print("[PASS] DELETE /api/services/{id} with active dependencies returned 409 and correct error message.")

        # Clean up the request context
        await request_context.dispose()

# Entry point for the async script
if __name__ == "__main__":
    asyncio.run(run())
