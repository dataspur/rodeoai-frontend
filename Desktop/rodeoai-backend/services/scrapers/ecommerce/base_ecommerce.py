"""
Base E-Commerce Scraper
Foundation for all western retail site scrapers.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductData:
    """Structured product data from e-commerce sites."""
    product_id: str
    name: str
    brand: str
    category: str

    # Pricing
    price: float
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    discount_percent: Optional[float] = None

    # Availability
    in_stock: bool = True
    stock_level: Optional[str] = None  # "low", "medium", "high", "out"
    sizes_available: List[str] = field(default_factory=list)
    colors_available: List[str] = field(default_factory=list)

    # Details
    url: str = ""
    image_url: str = ""
    description: str = ""
    sku: str = ""

    # Reviews
    rating: Optional[float] = None
    review_count: int = 0

    # Metadata
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    source: str = ""

    def to_dict(self) -> Dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "price": self.price,
            "original_price": self.original_price,
            "sale_price": self.sale_price,
            "discount_percent": self.discount_percent,
            "in_stock": self.in_stock,
            "stock_level": self.stock_level,
            "sizes_available": self.sizes_available,
            "colors_available": self.colors_available,
            "url": self.url,
            "image_url": self.image_url,
            "description": self.description[:500] if self.description else "",
            "sku": self.sku,
            "rating": self.rating,
            "review_count": self.review_count,
            "scraped_at": self.scraped_at.isoformat(),
            "source": self.source
        }


@dataclass
class PriceHistory:
    """Price history tracking."""
    product_id: str
    source: str
    prices: List[Dict] = field(default_factory=list)  # [{date, price, sale_price}]

    def add_price(self, price: float, sale_price: Optional[float] = None):
        self.prices.append({
            "date": datetime.utcnow().isoformat(),
            "price": price,
            "sale_price": sale_price
        })

    def get_price_trend(self) -> str:
        if len(self.prices) < 2:
            return "stable"
        recent = self.prices[-1]["price"]
        previous = self.prices[-2]["price"]
        if recent < previous:
            return "decreasing"
        elif recent > previous:
            return "increasing"
        return "stable"


class BaseEcommerceScraper(ABC):
    """Base class for all e-commerce scrapers."""

    SITE_NAME = "base"
    BASE_URL = ""

    # Category mappings
    CATEGORIES = {
        "boots": [],
        "hats": [],
        "jeans": [],
        "shirts": [],
        "outerwear": [],
        "accessories": [],
        "tack": [],
        "equipment": []
    }

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def init_browser(self):
        """Initialize Playwright browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def close(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()

    @abstractmethod
    async def scrape_product(self, url: str) -> Optional[ProductData]:
        """Scrape a single product page."""
        pass

    @abstractmethod
    async def scrape_category(self, category: str, limit: int = 100) -> List[ProductData]:
        """Scrape all products from a category."""
        pass

    @abstractmethod
    async def search_products(self, query: str, limit: int = 50) -> List[ProductData]:
        """Search for products."""
        pass

    async def scrape_all_categories(self, limit_per_category: int = 50) -> Dict[str, List[ProductData]]:
        """Scrape all configured categories."""
        results = {}
        for category in self.CATEGORIES.keys():
            try:
                products = await self.scrape_category(category, limit_per_category)
                results[category] = products
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error scraping category {category}: {e}")
                results[category] = []
        return results

    def parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float."""
        if not price_str:
            return None
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(cleaned)
        except ValueError:
            return None

    def calculate_discount(self, original: float, sale: float) -> float:
        """Calculate discount percentage."""
        if original <= 0:
            return 0
        return round((1 - sale / original) * 100, 1)

    async def get_page_content(self, url: str) -> Optional[str]:
        """Get page HTML content."""
        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            return await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
