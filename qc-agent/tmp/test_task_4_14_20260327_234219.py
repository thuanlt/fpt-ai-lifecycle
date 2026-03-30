import asyncio
import json
import time
from statistics import median

from playwright.async_api import async_playwright

# Replace with your actual API endpoint and valid credentials
LOGIN_URL = "https://example.com/api/login"
VALID_CREDENTIALS = {
    "username": "test_user",
    "password": "P@ssw0rd!"
}

async def perform_login(request_context, payload):
    """Send a single login request and return status code and elapsed time."""
    start_time = time.perf_counter()
    response = await request_context.post(
        LOGIN_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    elapsed = time.perf_counter() - start_time
    return response.status, elapsed

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        request_context = await context.new_request()

        # Create 100 concurrent login tasks
        tasks = [perform_login(request_context, VALID_CREDENTIALS) for _ in range(100)]
        results = await asyncio.gather(*tasks)

        statuses, times = zip(*results)

        # Assert all responses are 200 OK
        assert all(status == 200 for status in statuses), f"Not all responses were 200: {statuses}"

        # Calculate 95th percentile response time
        sorted_times = sorted(times)
        index_95 = int(0.95 * len(sorted_times)) - 1
        percentile_95 = sorted_times[index_95]
        print(f"95th percentile response time: {percentile_95:.3f} seconds")

        # Assert 95th percentile < 200 ms
        assert percentile_95 < 0.2, f"95th percentile response time {percentile_95:.3f}s exceeds 200ms"

        print("All assertions passed. Performance within limits.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
