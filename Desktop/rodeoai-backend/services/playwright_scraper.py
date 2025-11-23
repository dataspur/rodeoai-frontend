"""
Playwright Scraper
Modern async browser automation for reliable scraping.
Best for: Complex JS sites, multiple pages, reliable automation.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_scraper import BaseScraper, ScrapedPost, ScrapedProfile

# Playwright imports (async)
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PlaywrightScraper(BaseScraper):
    """
    Playwright-based async scraper for modern web applications.
    Features: Auto-wait, network interception, multiple browser support.
    """

    def __init__(self, browser_type: str = "chromium", headless: bool = True):
        super().__init__("playwright")
        self.browser_type = browser_type  # chromium, firefox, webkit
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    async def _ensure_browser(self) -> Browser:
        """Ensure browser is launched and return it."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Run: pip install playwright && playwright install")

        if self._browser is None or not self._browser.is_connected():
            self._playwright = await async_playwright().start()

            browser_launcher = getattr(self._playwright, self.browser_type)
            self._browser = await browser_launcher.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ] if self.browser_type == "chromium" else []
            )

        return self._browser

    async def _get_context(self) -> BrowserContext:
        """Get or create browser context with anti-detection."""
        if self._context is None:
            browser = await self._ensure_browser()
            self._context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US"
            )
            # Anti-detection script
            await self._context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        return self._context

    async def _new_page(self) -> Page:
        """Create a new page in the browser context."""
        context = await self._get_context()
        return await context.new_page()

    async def close(self):
        """Close browser and cleanup resources."""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a social media profile.
        Override in platform-specific subclasses.
        """
        self.logger.info(f"Generic profile scraping not implemented for: {username}")
        return None

    async def scrape_posts(self, username: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Scrape posts from a user.
        Override in platform-specific subclasses.
        """
        self.logger.info(f"Generic post scraping not implemented for: {username}")
        return []

    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Search for posts by keyword.
        Override in platform-specific subclasses.
        """
        self.logger.info(f"Generic search not implemented for: {query}")
        return []

    async def scrape_url(self, url: str, wait_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape content from a URL with full JavaScript rendering.

        Args:
            url: The URL to scrape
            wait_selector: Optional CSS selector to wait for before scraping
        """
        page = await self._new_page()

        try:
            # Navigate to URL
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=10000)

            # Get page info
            title = await page.title()

            # Get meta description
            description = await page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.content : null;
                }
            """)

            # Get Open Graph data
            og_data = await page.evaluate("""
                () => ({
                    title: document.querySelector('meta[property="og:title"]')?.content,
                    description: document.querySelector('meta[property="og:description"]')?.content,
                    image: document.querySelector('meta[property="og:image"]')?.content
                })
            """)

            # Get all text content
            text_content = await page.evaluate("() => document.body.innerText")

            # Get links
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]'))
                    .slice(0, 30)
                    .map(a => ({
                        href: a.href,
                        text: a.innerText.trim().substring(0, 100)
                    }))
                    .filter(l => l.href && l.text)
            """)

            # Get images
            images = await page.evaluate("""
                () => Array.from(document.querySelectorAll('img[src]'))
                    .slice(0, 15)
                    .map(img => ({
                        src: img.src,
                        alt: img.alt || ''
                    }))
            """)

            return {
                "url": url,
                "status_code": response.status if response else None,
                "title": title,
                "description": description,
                "og_data": og_data,
                "text_content": text_content[:10000],
                "links": links,
                "images": images,
                "rendered": True,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return {"error": str(e), "url": url}
        finally:
            await page.close()

    async def take_screenshot(self, url: str, output_path: str, full_page: bool = True) -> bool:
        """Take a screenshot of a webpage."""
        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.screenshot(path=output_path, full_page=full_page)
            return True
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return False
        finally:
            await page.close()

    async def generate_pdf(self, url: str, output_path: str) -> bool:
        """Generate PDF of a webpage (Chromium only)."""
        if self.browser_type != "chromium":
            self.logger.warning("PDF generation only works with Chromium")
            return False

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.pdf(path=output_path, format="A4")
            return True
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return False
        finally:
            await page.close()

    async def scroll_and_collect(
        self,
        url: str,
        scroll_count: int = 5,
        item_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load page, scroll to load dynamic content, and optionally collect items.

        Args:
            url: URL to scrape
            scroll_count: Number of times to scroll
            item_selector: Optional CSS selector for items to collect
        """
        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            items_collected = []
            previous_height = 0

            for i in range(scroll_count):
                # Scroll to bottom
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.5)  # Wait for content

                # Check scroll progress
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                previous_height = current_height

                # Collect items if selector provided
                if item_selector:
                    new_items = await page.evaluate(f"""
                        () => Array.from(document.querySelectorAll('{item_selector}'))
                            .map(el => el.innerText.trim())
                    """)
                    items_collected.extend(new_items)

            # Get final text content
            text_content = await page.evaluate("() => document.body.innerText")

            return {
                "url": url,
                "scrolls_performed": i + 1,
                "final_height": current_height,
                "items_found": len(set(items_collected)) if items_collected else None,
                "items": list(set(items_collected))[:100] if items_collected else None,
                "text_content": text_content[:15000],
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "url": url}
        finally:
            await page.close()

    async def intercept_network(
        self,
        url: str,
        resource_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Load page and intercept network requests.
        Useful for finding API endpoints and data sources.

        Args:
            url: URL to load
            resource_types: List of resource types to capture (xhr, fetch, document, etc.)
        """
        page = await self._new_page()
        captured_requests = []

        if resource_types is None:
            resource_types = ["xhr", "fetch"]

        async def handle_request(request):
            if request.resource_type in resource_types:
                captured_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "headers": dict(request.headers)
                })

        page.on("request", handle_request)

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # Wait for additional requests

            return {
                "url": url,
                "captured_requests": captured_requests,
                "request_count": len(captured_requests),
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "url": url}
        finally:
            await page.close()

    async def fill_form_and_submit(
        self,
        url: str,
        form_data: Dict[str, str],
        submit_selector: str
    ) -> Dict[str, Any]:
        """
        Fill out a form and submit it.

        Args:
            url: URL with the form
            form_data: Dict mapping selectors to values to fill
            submit_selector: Selector for submit button
        """
        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Fill form fields
            for selector, value in form_data.items():
                await page.fill(selector, value)

            # Submit form
            await page.click(submit_selector)
            await page.wait_for_load_state("networkidle")

            # Get result page content
            title = await page.title()
            text_content = await page.evaluate("() => document.body.innerText")

            return {
                "url": page.url,
                "title": title,
                "text_content": text_content[:10000],
                "success": True,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "url": url, "success": False}
        finally:
            await page.close()
