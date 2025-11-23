"""
BeautifulSoup Scraper
Lightweight HTML parsing scraper for static content.
Best for: Simple HTML pages, news sites, blogs, public profiles.
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

from .base_scraper import BaseScraper, ScrapedPost, ScrapedProfile


class BeautifulSoupScraper(BaseScraper):
    """
    Lightweight scraper using BeautifulSoup for HTML parsing.
    Best for static HTML content that doesn't require JavaScript rendering.
    """

    def __init__(self):
        super().__init__("beautifulsoup")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        try:
            session = await self._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"Failed to fetch {url}: Status {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str, parser: str = "lxml") -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, parser)

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a public profile.
        Note: Most social media profiles require JS rendering.
        This works best with public pages that have server-rendered content.
        """
        self.logger.info(f"BeautifulSoup is limited for dynamic social profiles. Consider using Selenium/Playwright.")
        return None

    async def scrape_posts(self, username: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Scrape posts from a user.
        Note: Most social media feeds require JS rendering.
        """
        self.logger.info(f"BeautifulSoup is limited for dynamic feeds. Consider using Selenium/Playwright.")
        return []

    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Search for posts by keyword.
        Note: Most social media search requires JS rendering.
        """
        self.logger.info(f"BeautifulSoup is limited for dynamic search. Consider using Selenium/Playwright.")
        return []

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape generic content from any URL.
        Extracts title, meta description, headings, paragraphs, links, and images.
        """
        html = await self.fetch_html(url)
        if not html:
            return {"error": "Failed to fetch URL", "url": url}

        soup = self.parse_html(html)

        # Extract metadata
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else None

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content") if meta_desc else None

        # Open Graph metadata
        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        og_image = soup.find("meta", attrs={"property": "og:image"})

        # Extract main content
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for heading in soup.find_all(tag)[:5]:
                headings.append({
                    "level": tag,
                    "text": heading.get_text(strip=True)
                })

        # Extract paragraphs (limit to main content)
        paragraphs = []
        for p in soup.find_all("p")[:10]:
            text = p.get_text(strip=True)
            if len(text) > 50:  # Only meaningful paragraphs
                paragraphs.append(text[:500])  # Truncate long paragraphs

        # Extract links
        links = []
        for a in soup.find_all("a", href=True)[:20]:
            href = a.get("href")
            text = a.get_text(strip=True)
            if href and not href.startswith("#"):
                links.append({"href": href, "text": text[:100] if text else ""})

        # Extract images
        images = []
        for img in soup.find_all("img", src=True)[:10]:
            src = img.get("src")
            alt = img.get("alt", "")
            if src:
                images.append({"src": src, "alt": alt})

        return {
            "url": url,
            "title": title_text,
            "description": description,
            "og_data": {
                "title": og_title.get("content") if og_title else None,
                "description": og_desc.get("content") if og_desc else None,
                "image": og_image.get("content") if og_image else None
            },
            "headings": headings,
            "paragraphs": paragraphs,
            "links": links,
            "images": images,
            "scraped_at": datetime.utcnow().isoformat()
        }

    async def scrape_article(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from a news/blog URL.
        Uses heuristics to find main article content.
        """
        html = await self.fetch_html(url)
        if not html:
            return {"error": "Failed to fetch URL", "url": url}

        soup = self.parse_html(html)

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
            element.decompose()

        # Try to find article container
        article = soup.find("article")
        if not article:
            # Try common content containers
            article = soup.find("div", class_=re.compile(r"(article|content|post|entry)", re.I))
        if not article:
            article = soup.find("main")
        if not article:
            article = soup.body

        # Extract text content
        if article:
            text_content = article.get_text(separator="\n", strip=True)
            # Clean up multiple newlines
            text_content = re.sub(r'\n{3,}', '\n\n', text_content)
        else:
            text_content = ""

        # Extract author
        author = None
        author_elem = soup.find(class_=re.compile(r"(author|byline)", re.I))
        if author_elem:
            author = author_elem.get_text(strip=True)

        # Extract publish date
        publish_date = None
        date_elem = soup.find("time")
        if date_elem:
            publish_date = date_elem.get("datetime") or date_elem.get_text(strip=True)

        return {
            "url": url,
            "title": soup.find("title").get_text(strip=True) if soup.find("title") else None,
            "author": author,
            "publish_date": publish_date,
            "content": text_content[:10000],  # Limit content length
            "word_count": len(text_content.split()),
            "scraped_at": datetime.utcnow().isoformat()
        }
