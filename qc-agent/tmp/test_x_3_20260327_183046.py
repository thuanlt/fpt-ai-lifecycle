import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # TODO: Replace with the actual URL of the Dashboard screen
        await page.goto("http://localhost:3000/dashboard")

        # Select all heading elements (H1, H2, H3) on the page
        headings = await page.query_selector_all("h1, h2, h3")
        for heading in headings:
            # Retrieve the tag name (e.g., H1, H2, H3)
            tag = await heading.evaluate("el => el.tagName")

            # Get computed CSS styles for the heading element
            style = await heading.evaluate(
                """
                el => {
                    const cs = window.getComputedStyle(el);
                    return {
                        fontFamily: cs.fontFamily,
                        fontWeight: cs.fontWeight,
                        fontSize: cs.fontSize,
                        lineHeight: cs.lineHeight,
                        letterSpacing: cs.letterSpacing
                    };
                }
                """
            )

            # Define expected design‑system tokens per heading level
            if tag == "H1":
                expected = {
                    "fontFamily": "Inter",
                    "fontWeight": "700",   # Bold
                    "fontSize": "24px",
                    # Add expected line‑height & letter‑spacing if known
                }
            elif tag == "H2":
                expected = {
                    "fontFamily": "Inter",
                    "fontWeight": "600",
                    "fontSize": "20px",
                }
            else:  # H3
                expected = {
                    "fontFamily": "Inter",
                    "fontWeight": "500",
                    "fontSize": "18px",
                }

            # Assertions – will raise AssertionError if any check fails
            assert expected["fontFamily"] in style["fontFamily"], f"{tag} fontFamily mismatch: {style['fontFamily']}"
            assert style["fontWeight"] == expected["fontWeight"], f"{tag} fontWeight mismatch: {style['fontWeight']}"
            assert style["fontSize"] == expected["fontSize"], f"{tag} fontSize mismatch: {style['fontSize']}"
            # Optional: add line‑height & letter‑spacing checks here when token values are defined

        await browser.close()

asyncio.run(run())
