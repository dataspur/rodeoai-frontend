"""
Selenium Scraper
Browser automation scraper for JavaScript-rendered content.
Best for: Dynamic pages, login-required content, complex interactions.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from .base_scraper import BaseScraper, ScrapedPost, ScrapedProfile


class SeleniumScraper(BaseScraper):
    """
    Selenium-based scraper for JavaScript-rendered content.
    Uses Chrome in headless mode for browser automation.
    """

    def __init__(self, headless: bool = True):
        super().__init__("selenium")
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None

    def _create_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome WebDriver."""
        options = Options()

        if self.headless:
            options.add_argument("--headless=new")

        # Essential options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # User agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Fallback without webdriver-manager
            driver = webdriver.Chrome(options=options)

        # Additional anti-detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })

        return driver

    def _get_driver(self) -> webdriver.Chrome:
        """Get or create WebDriver instance."""
        if self.driver is None:
            self.driver = self._create_driver()
        return self.driver

    async def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for an element to be present."""
        driver = self._get_driver()
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))

    def _safe_find(self, by: By, value: str, parent=None):
        """Safely find an element, returning None if not found."""
        try:
            element = parent if parent else self._get_driver()
            return element.find_element(by, value)
        except NoSuchElementException:
            return None

    def _safe_find_all(self, by: By, value: str, parent=None) -> List:
        """Safely find all elements."""
        try:
            element = parent if parent else self._get_driver()
            return element.find_elements(by, value)
        except NoSuchElementException:
            return []

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a social media profile.
        This is a generic implementation - override for specific platforms.
        """
        self.logger.info(f"Generic profile scraping for: {username}")
        return None

    async def scrape_posts(self, username: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Scrape posts from a user.
        This is a generic implementation - override for specific platforms.
        """
        self.logger.info(f"Generic post scraping for: {username}")
        return []

    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Search for posts by keyword.
        This is a generic implementation - override for specific platforms.
        """
        self.logger.info(f"Generic search for: {query}")
        return []

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL with full JavaScript rendering.
        """
        driver = self._get_driver()

        try:
            driver.get(url)
            # Wait for page to load
            await asyncio.sleep(2)

            # Wait for body to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Get page source after JS rendering
            page_source = driver.page_source

            # Extract basic info
            title = driver.title

            # Try to get meta description
            description = None
            try:
                meta = driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
                description = meta.get_attribute("content")
            except NoSuchElementException:
                pass

            # Get all text content
            body = driver.find_element(By.TAG_NAME, "body")
            text_content = body.text

            # Get all links
            links = []
            for a in driver.find_elements(By.TAG_NAME, "a")[:30]:
                try:
                    href = a.get_attribute("href")
                    text = a.text.strip()
                    if href and text:
                        links.append({"href": href, "text": text[:100]})
                except Exception:
                    pass

            # Get all images
            images = []
            for img in driver.find_elements(By.TAG_NAME, "img")[:15]:
                try:
                    src = img.get_attribute("src")
                    alt = img.get_attribute("alt") or ""
                    if src:
                        images.append({"src": src, "alt": alt})
                except Exception:
                    pass

            return {
                "url": url,
                "title": title,
                "description": description,
                "text_content": text_content[:10000],
                "links": links,
                "images": images,
                "rendered": True,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except TimeoutException:
            return {"error": "Page load timeout", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}

    async def take_screenshot(self, url: str, output_path: str) -> bool:
        """Take a screenshot of a webpage."""
        driver = self._get_driver()

        try:
            driver.get(url)
            await asyncio.sleep(2)  # Wait for page load
            driver.save_screenshot(output_path)
            return True
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return False

    async def scroll_and_collect(self, url: str, scroll_count: int = 3) -> Dict[str, Any]:
        """
        Load a page and scroll to load dynamic content.
        Useful for infinite scroll pages.
        """
        driver = self._get_driver()

        try:
            driver.get(url)
            await asyncio.sleep(2)

            collected_items = []
            last_height = driver.execute_script("return document.body.scrollHeight")

            for i in range(scroll_count):
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1.5)  # Wait for content to load

                # Check if we've reached the bottom
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Get final page content
            return {
                "url": url,
                "scrolls_performed": i + 1,
                "final_height": last_height,
                "text_content": driver.find_element(By.TAG_NAME, "body").text[:15000],
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "url": url}

    async def execute_script(self, url: str, script: str) -> Any:
        """
        Load a page and execute custom JavaScript.
        Returns the script's return value.
        """
        driver = self._get_driver()

        try:
            driver.get(url)
            await asyncio.sleep(2)
            result = driver.execute_script(script)
            return {"result": result, "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}
