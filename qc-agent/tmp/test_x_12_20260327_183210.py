import asyncio
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch a headless browser (Chromium). Adjust launch options if needed.
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # ---------------------------------------------------------------------
        # STEP 1: Send a request to the Design System API endpoint.
        # Replace the placeholder URL with the actual endpoint that returns the
        # design‑system JSON payload containing the `version` field.
        # ---------------------------------------------------------------------
        api_url = "https://example.com/api/design-system"  # <-- TODO: update URL
        response = await context.request.get(api_url)
        assert response.ok, f"API request failed with status {response.status}"

        # ---------------------------------------------------------------------
        # STEP 2: Parse the JSON response and extract the `version` field.
        # ---------------------------------------------------------------------
        data = await response.json()
        version = data.get("version")
        assert version is not None, "Version field missing in API response"

        # ---------------------------------------------------------------------
        # STEP 3: Validate that the version follows Semantic Versioning (e.g., v1.2.3).
        # ---------------------------------------------------------------------
        semver_regex = r"^v?(\d+)\.(\d+)\.(\d+)$"
        assert re.match(semver_regex, version), (
            f"Version '{version}' does not conform to semantic versioning"
        )

        # If the script reaches this point, the test passes.
        print(f"✅ Version '{version}' is present and follows semantic versioning.")

        await browser.close()

# Entry point for the async script.
asyncio.run(main())
