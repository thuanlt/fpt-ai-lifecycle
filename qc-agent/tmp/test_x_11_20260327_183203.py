import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Send GET request to the design‑system endpoint
        # Adjust the base URL as needed for the environment under test
        response = await page.request.get("http://localhost/api/design-system")
        
        # Verify HTTP status code
        assert response.status == 200, f"Expected status 200, got {response.status}"
        
        # Parse JSON payload
        data = await response.json()
        
        # Verify that required token groups are present
        required_keys = ["color", "typography", "shape", "elevation"]
        for key in required_keys:
            assert key in data, f"Missing '{key}' in design system payload"
        
        print("Test passed: Design system token set is complete.")
        
        await browser.close()

asyncio.run(main())
