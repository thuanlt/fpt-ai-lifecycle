import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        base_url = "https://api.example.com"  # replace with actual base URL
        url = f"{base_url}/login"
        payload = {
            "username": "a" * 256,
            "password": "TestPassword123!"
        }
        response = await page.request.post(url, data=payload)
        assert response.status == 400, f"Expected status 400, got {response.status}"
        json_body = await response.json()
        assert "error" in json_body, "Response JSON does not contain 'error' key"
        assert json_body["error"] == "username exceeds maximum length", f"Unexpected error message: {json_body['error']}"
        print("Test passed: Username exceeds max length returns 400 with correct error message.")
        await browser.close()

asyncio.run(run())