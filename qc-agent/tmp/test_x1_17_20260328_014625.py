import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser (set headless=True for CI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ------------------------------------------------------------
        # 1. Navigate to the application (replace with actual URL)
        # ------------------------------------------------------------
        await page.goto("https://example.com")

        # ------------------------------------------------------------
        # 2. Go to Cart page – assuming the user already has items
        # ------------------------------------------------------------
        await page.goto("https://example.com/cart")

        # ------------------------------------------------------------
        # 3. Click "Proceed to Checkout"
        # ------------------------------------------------------------
        await page.click('text="Proceed to Checkout"')

        # ------------------------------------------------------------
        # 4. Verify navigation to "Shipping Information" step
        # ------------------------------------------------------------
        await page.wait_for_selector('text="Shipping Information"', timeout=5000)

        # ------------------------------------------------------------
        # 5. Fill required shipping fields (adjust selectors as needed)
        # ------------------------------------------------------------
        await page.fill('input[name="address"]', "123 Main St")
        await page.fill('input[name="city"]', "Metropolis")
        await page.fill('input[name="zip"]', "12345")
        await page.fill('input[name="country"]', "USA")

        # ------------------------------------------------------------
        # 6. Verify "Continue to Payment" button appears and click it
        # ------------------------------------------------------------
        await page.wait_for_selector('text="Continue to Payment"', timeout=5000)
        await page.click('text="Continue to Payment"')

        # ------------------------------------------------------------
        # 7. Payment step – fill dummy card details
        # ------------------------------------------------------------
        await page.wait_for_selector('text="Payment Information"', timeout=5000)
        await page.fill('input[name="cardNumber"]', "4111111111111111")
        await page.fill('input[name="expiry"]', "12/30")
        await page.fill('input[name="cvc"]', "123")
        await page.click('text="Pay Now"')

        # ------------------------------------------------------------
        # 8. Verify Order Confirmation page and capture order number
        # ------------------------------------------------------------
        await page.wait_for_selector('text="Order Confirmation"', timeout=5000)
        # Assuming order number is rendered inside an element with class .order-number
        order_number = await page.text_content('.order-number')
        print(f"Order placed successfully. Order number: {order_number}")

        await browser.close()

asyncio.run(run())
