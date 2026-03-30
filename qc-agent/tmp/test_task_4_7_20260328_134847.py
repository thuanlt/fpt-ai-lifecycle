import asyncio
from playwright.async_api import async_playwright

async def main():
    # Base URL of the API under test – adjust as needed
    base_url = "http://localhost:8000"

    async with async_playwright() as p:
        # Create a request context for API calls
        request_context = await p.request.new_context(base_url=base_url)

        # -----------------------------------------------------------------
        # 1. Obtain authentication token via the login endpoint
        # -----------------------------------------------------------------
        login_payload = {
            "username": "testuser",
            "password": "testpass"
        }
        login_response = await request_context.post("/api/login", data=login_payload)
        assert login_response.ok, f"Login request failed with status {login_response.status}"
        login_json = await login_response.json()
        token = login_json.get("token")
        assert token, "Token not present in login response"
        print(f"Obtained token: {token}")

        # -----------------------------------------------------------------
        # 2. Access protected resource with the token – expect HTTP 200
        # -----------------------------------------------------------------
        auth_headers = {"Authorization": f"Bearer {token}"}
        profile_response = await request_context.get("/api/user/profile", headers=auth_headers)
        assert profile_response.status == 200, (
            f"Expected 200 OK when token is provided, got {profile_response.status}"
        )
        profile_data = await profile_response.json()
        print("Protected resource accessed successfully. Profile data:")
        print(profile_data)

        # -----------------------------------------------------------------
        # 3. Access protected resource without token – expect HTTP 401
        # -----------------------------------------------------------------
        profile_no_token = await request_context.get("/api/user/profile")
        assert profile_no_token.status == 401, (
            f"Expected 401 Unauthorized when token is missing, got {profile_no_token.status}"
        )
        print("Unauthenticated request correctly returned 401 Unauthorized.")

        # Clean up the request context
        await request_context.dispose()

if __name__ == "__main__":
    asyncio.run(main())
