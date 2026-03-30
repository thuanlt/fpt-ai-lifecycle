import asyncio
from playwright.async_api import async_playwright, expect

# ---------------------------------------------------------------------------
# Configuration – replace these values with the actual application details
# ---------------------------------------------------------------------------
BASE_URL = "https://example.com"  # <-- your application URL
USERNAME = "test_user@example.com"
PASSWORD = "Password123!"

# Shipping information – adjust selectors/values as needed for the target app
SHIPPING_INFO = {
    "name": "John Doe",
    "address": "123 Main St",
    "city": "Hanoi",
    "zip": "100000",
    "country": "Vietnam",
    "phone": "0123456789",
}

# Selectors – these are placeholders; replace with real selectors from the UI
SELECTORS = {
    "login_email": "input[name='email']",
    "login_password": "input[name='password']",
    "login_button": "button[type='submit']",
    "shipping_name": "#shipping-name",
    "shipping_address": "#shipping-address",
    "shipping_city": "#shipping-city",
    "shipping_zip": "#shipping-zip",
    "shipping_country": "#shipping-country",
    "shipping_phone": "#shipping-phone",
    "payment_method": "input[name='payment'][value='credit_card']",  # example
    "confirm_order_button": "button#confirm-order",
    "order_id": "#order-id",
    "order_summary": "#order-summary",
    "estimated_delivery": "#estimated-delivery",
}

async def login(page):
    await page.goto(f"{BASE_URL}/login")
    await page.fill(SELECTORS["login_email"], USERNAME)
    await page.fill(SELECTORS["login_password"], PASSWORD)
    await page.click(SELECTORS["login_button"])
    # Wait for navigation after login – adjust as needed
    await page.wait_for_load_state("networkidle")

async def fill_shipping_information(page):
    await page.fill(SELECTORS["shipping_name"], SHIPPING_INFO["name"])
    await page.fill(SELECTORS["shipping_address"], SHIPPING_INFO["address"])
    await page.fill(SELECTORS["shipping_city"], SHIPPING_INFO["city"])
    await page.fill(SELECTORS["shipping_zip"], SHIPPING_INFO["zip"])
    await page.fill(SELECTORS["shipping_country"], SHIPPING_INFO["country"])
    await page.fill(SELECTORS["shipping_phone"], SHIPPING_INFO["phone"])

async def select_payment_method(page):
    await page.check(SELECTORS["payment_method"])

async def confirm_order(page):
    await page.click(SELECTORS["confirm_order_button"])
    # Wait for the confirmation page to load
    await page.wait_for_selector(SELECTORS["order_id"], timeout=15000)

async def verify_confirmation(page):
    # Verify Order ID is generated and not empty
    order_id_element = await page.wait_for_selector(SELECTORS["order_id"])
    order_id = await order_id_element.text_content()
    assert order_id and order_id.strip(), "Order ID was not generated"

    # Verify order summary is displayed
    summary_element = await page.wait_for_selector(SELECTORS["order_summary"])
    summary_text = await summary_element.text_content()
    assert summary_text and "Order Summary" in summary_text, "Order summary not displayed"

    # Verify estimated delivery date is shown
    delivery_element = await page.wait_for_selector(SELECTORS["estimated_delivery"])
    delivery_text = await delivery_element.text_content()
    assert delivery_text and "Estimated Delivery" in delivery_text, "Estimated delivery information missing"

    # Note: Confirmation email verification typically requires access to an email inbox.
    # This script does not perform email validation; it assumes the backend sends the email.

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for CI
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Log in (if authentication is required)
        await login(page)

        # 2. Navigate to the checkout page – adjust URL as needed
        await page.goto(f"{BASE_URL}/checkout")
        await page.wait_for_load_state("networkidle")

        # 3. Fill shipping information
        await fill_shipping_information(page)

        # 4. Select a payment method
        await select_payment_method(page)

        # 5. Confirm the order
        await confirm_order(page)

        # 6. Verify order confirmation details
        await verify_confirmation(page)

        print("✅ End‑to‑end order creation test passed.")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
