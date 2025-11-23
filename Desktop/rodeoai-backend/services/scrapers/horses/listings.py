"""
Horse Listing Scrapers
Scrapes horse for sale listings from various sources.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class HorseListing:
    """Horse for sale listing data."""
    title: str
    horse_name: str = ""
    price: float = 0.0
    price_text: str = ""  # "Asking $45,000", "Price negotiable", etc.

    # Horse details
    age: int = 0
    sex: str = ""
    color: str = ""
    height: str = ""
    breed: str = "Quarter Horse"

    # Pedigree
    sire: str = ""
    dam: str = ""

    # Performance
    discipline: str = ""  # cutting, reining, roping, etc.
    experience_level: str = ""  # finished, started, prospect, etc.
    earnings: float = 0.0
    show_record: str = ""

    # Seller info
    seller_name: str = ""
    seller_location: str = ""
    seller_contact: str = ""

    # Listing info
    listing_url: str = ""
    source: str = ""
    posted_date: Optional[datetime] = None
    images: List[str] = field(default_factory=list)
    video_url: str = ""

    description: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "horse_name": self.horse_name,
            "price": self.price,
            "price_text": self.price_text,
            "age": self.age,
            "sex": self.sex,
            "color": self.color,
            "height": self.height,
            "breed": self.breed,
            "sire": self.sire,
            "dam": self.dam,
            "discipline": self.discipline,
            "experience_level": self.experience_level,
            "earnings": self.earnings,
            "show_record": self.show_record,
            "seller_name": self.seller_name,
            "seller_location": self.seller_location,
            "listing_url": self.listing_url,
            "source": self.source,
            "posted_date": self.posted_date.isoformat() if self.posted_date else "",
            "images": self.images[:5],
            "video_url": self.video_url,
            "description": self.description[:1000],
            "scraped_at": self.scraped_at.isoformat()
        }


class HorseListingScraper:
    """Scraper for horse listing sites."""

    LISTING_SITES = {
        "equine": "https://www.equine.com",
        "dreamhorse": "https://www.dreamhorse.com",
        "horseclicks": "https://www.horseclicks.com",
        "equinenow": "https://www.equinenow.com"
    }

    CUTTING_KEYWORDS = [
        "cutting", "cutter", "ncha", "cowhorse", "cow horse",
        "reined cow horse", "nrcha", "fence work"
    ]

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def init_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def close(self):
        if self.browser:
            await self.browser.close()

    async def search_cutting_horses(self, limit: int = 50) -> List[HorseListing]:
        """Search for cutting horses across all sources."""
        all_listings = []

        for source, base_url in self.LISTING_SITES.items():
            try:
                listings = await self._search_site(
                    source,
                    base_url,
                    query="cutting horse",
                    limit=limit // len(self.LISTING_SITES)
                )
                all_listings.extend(listings)
            except Exception as e:
                logger.error(f"Error searching {source}: {e}")
                continue

        return all_listings[:limit]

    async def _search_site(
        self,
        source: str,
        base_url: str,
        query: str,
        limit: int = 20
    ) -> List[HorseListing]:
        """Search a specific listing site."""
        listings = []

        url = f"{base_url}/search?q={query.replace(' ', '+')}"

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching {source}: {e}")
            return listings

        soup = BeautifulSoup(html, 'html.parser')

        listing_cards = soup.select('.listing-card, .horse-listing, .search-result, .ad-card')[:limit]

        for card in listing_cards:
            try:
                title_elem = card.select_one('.title, .listing-title, h2, h3')
                price_elem = card.select_one('.price, .listing-price')
                location_elem = card.select_one('.location, .seller-location')
                link = card.select_one('a[href]')
                img = card.select_one('img')

                # Extract price
                price_text = price_elem.get_text(strip=True) if price_elem else ""
                price = self._parse_price(price_text)

                # Extract details from title/description
                title = title_elem.get_text(strip=True) if title_elem else ""
                details = self._extract_details_from_text(title)

                listings.append(HorseListing(
                    title=title,
                    price=price,
                    price_text=price_text,
                    sex=details.get("sex", ""),
                    age=details.get("age", 0),
                    color=details.get("color", ""),
                    seller_location=location_elem.get_text(strip=True) if location_elem else "",
                    listing_url=link.get('href') if link else "",
                    images=[img.get('src')] if img and img.get('src') else [],
                    source=source,
                    discipline="cutting"
                ))

            except Exception as e:
                logger.error(f"Error parsing listing: {e}")
                continue

        return listings

    async def get_listing_details(self, url: str) -> Optional[HorseListing]:
        """Get full details for a specific listing."""
        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching listing: {e}")
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            title = soup.select_one('h1, .listing-title')
            price = soup.select_one('.price, .listing-price')
            description = soup.select_one('.description, .listing-description')

            # Horse details
            name = soup.select_one('.horse-name, [itemprop="name"]')
            age = soup.select_one('.age, .horse-age')
            sex = soup.select_one('.sex, .horse-sex, .gender')
            color = soup.select_one('.color, .horse-color')
            height = soup.select_one('.height, .horse-height')
            breed = soup.select_one('.breed, .horse-breed')

            # Pedigree
            sire = soup.select_one('.sire, .horse-sire')
            dam = soup.select_one('.dam, .horse-dam')

            # Seller
            seller = soup.select_one('.seller-name, .contact-name')
            location = soup.select_one('.location, .seller-location')

            # Media
            images = [img.get('src') for img in soup.select('.gallery img, .listing-images img') if img.get('src')]
            video = soup.select_one('video source, iframe[src*="youtube"], iframe[src*="vimeo"]')

            price_text = price.get_text(strip=True) if price else ""

            return HorseListing(
                title=title.get_text(strip=True) if title else "",
                horse_name=name.get_text(strip=True) if name else "",
                price=self._parse_price(price_text),
                price_text=price_text,
                age=int(re.sub(r'\D', '', age.get_text())) if age and re.search(r'\d', age.get_text()) else 0,
                sex=sex.get_text(strip=True) if sex else "",
                color=color.get_text(strip=True) if color else "",
                height=height.get_text(strip=True) if height else "",
                breed=breed.get_text(strip=True) if breed else "Quarter Horse",
                sire=sire.get_text(strip=True) if sire else "",
                dam=dam.get_text(strip=True) if dam else "",
                seller_name=seller.get_text(strip=True) if seller else "",
                seller_location=location.get_text(strip=True) if location else "",
                listing_url=url,
                images=images[:10],
                video_url=video.get('src') if video else "",
                description=description.get_text(strip=True) if description else "",
                source=self._detect_source(url)
            )

        except Exception as e:
            logger.error(f"Error parsing listing details: {e}")
            return None

    def _parse_price(self, price_text: str) -> float:
        """Extract numeric price from text."""
        if not price_text:
            return 0.0
        match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', price_text)
        if match:
            return float(match.group(1).replace(',', ''))
        return 0.0

    def _extract_details_from_text(self, text: str) -> Dict:
        """Extract horse details from title/description text."""
        details = {}

        text_lower = text.lower()

        # Sex
        if "mare" in text_lower:
            details["sex"] = "Mare"
        elif "gelding" in text_lower:
            details["sex"] = "Gelding"
        elif "stallion" in text_lower:
            details["sex"] = "Stallion"

        # Age
        age_match = re.search(r'(\d+)\s*(?:year|yr|yo)', text_lower)
        if age_match:
            details["age"] = int(age_match.group(1))

        # Color
        colors = ["bay", "sorrel", "chestnut", "palomino", "buckskin", "gray", "grey",
                  "black", "roan", "dun", "grulla", "cremello", "perlino"]
        for color in colors:
            if color in text_lower:
                details["color"] = color.title()
                break

        return details

    def _detect_source(self, url: str) -> str:
        """Detect listing source from URL."""
        for source, base_url in self.LISTING_SITES.items():
            if base_url.replace("https://www.", "") in url:
                return source
        return "unknown"

    async def search_by_price_range(
        self,
        min_price: float,
        max_price: float,
        discipline: str = "cutting",
        limit: int = 50
    ) -> List[HorseListing]:
        """Search for horses within a price range."""
        all_listings = await self.search_cutting_horses(limit * 2)

        filtered = [
            listing for listing in all_listings
            if min_price <= listing.price <= max_price
        ]

        return filtered[:limit]

    async def search_prospects(self, limit: int = 30) -> List[HorseListing]:
        """Search for cutting horse prospects."""
        all_listings = []

        for source, base_url in self.LISTING_SITES.items():
            try:
                listings = await self._search_site(
                    source,
                    base_url,
                    query="cutting prospect",
                    limit=limit // len(self.LISTING_SITES)
                )
                all_listings.extend(listings)
            except Exception:
                continue

        return all_listings[:limit]
