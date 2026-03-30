import asyncio
import os
import sys
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright
from mcp.server.fastmcp import FastMCP

# Create a Model-Context-Protocol (MCP) server for Playwright
mcp = FastMCP("Playwright")

# Global state for browser
_playwright = None
_browser = None
_context = None
_page = None

async def get_page():
    global _playwright, _browser, _context, _page
    if not _page:
        if not _playwright:
            _playwright = await async_playwright().start()
        if not _browser:
            _browser = await _playwright.chromium.launch(headless=True)
            _context = await _browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
        if not _page:
            _page = await _context.new_page()
    return _page

@mcp.tool()
async def browser_navigate(url: str) -> str:
    """Navigate the browser to a specific URL."""
    page = await get_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Error navigating to {url}: {str(e)}"

@mcp.tool()
async def browser_click(selector: str) -> str:
    """Click an element on the current page using a CSS selector."""
    page = await get_page()
    try:
        await page.click(selector, timeout=10000)
        return f"Successfully clicked: {selector}"
    except Exception as e:
        return f"Error clicking {selector}: {str(e)}"

@mcp.tool()
async def browser_fill(selector: str, value: str) -> str:
    """Fill an input field with text."""
    page = await get_page()
    try:
        await page.fill(selector, value, timeout=10000)
        return f"Successfully filled {selector}"
    except Exception as e:
        return f"Error filling {selector}: {str(e)}"

@mcp.tool()
async def browser_press(key: str) -> str:
    """Press a keyboard key (e.g., 'Enter', 'Tab', 'Escape')."""
    page = await get_page()
    try:
        await page.keyboard.press(key)
        return f"Pressed {key}"
    except Exception as e:
        return f"Error pressing {key}: {str(e)}"

@mcp.tool()
async def browser_hover(selector: str) -> str:
    """Hover over an element."""
    page = await get_page()
    try:
        await page.hover(selector, timeout=5000)
        return f"Hovered over {selector}"
    except Exception as e:
        return f"Error hovering over {selector}: {str(e)}"

@mcp.tool()
async def browser_get_content() -> str:
    """Get the visible text content of the current page."""
    page = await get_page()
    try:
        content = await page.evaluate("() => document.body.innerText")
        return content[:15000]
    except Exception as e:
        return f"Error getting content: {str(e)}"

@mcp.tool()
async def browser_list_links() -> List[Dict[str, str]]:
    """List all the links (text and href) on the current page."""
    page = await get_page()
    try:
        links = await page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a'));
            return anchors.map(a => ({
                text: a.innerText.trim(),
                href: a.href
            })).filter(a => a.text && a.href && !a.href.startsWith('javascript:'));
        }""")
        return links
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
async def browser_screenshot(name: str = "screenshot") -> str:
    """Chụp ảnh màn hình lưu vào thư mục tmp."""
    page = await get_page()
    try:
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        path = os.path.join(tmp_dir, f"{name}.png")
        await page.screenshot(path=path)
        return f"Screenshot saved to {path}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

@mcp.tool()
async def browser_wait_for(selector: str, timeout: int = 10000) -> str:
    """Wait for an element to appear on the page."""
    page = await get_page()
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return f"Element {selector} appeared."
    except Exception as e:
        return f"Timeout waiting for {selector}."

async def create_stdio_streams():
    import anyio
    c_write, s_read = anyio.create_memory_object_stream(50)
    s_write, c_read = anyio.create_memory_object_stream(50)
    async def run_server_task():
        await mcp._mcp_server.run(
            s_read,
            s_write,
            mcp._mcp_server.create_initialization_options()
        )
    asyncio.create_task(run_server_task())
    return c_read, c_write

if __name__ == "__main__":
    mcp.run(transport='sse', port=8931)
