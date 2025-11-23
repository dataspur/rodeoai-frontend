"""
Horse Sale Scrapers
Scrapes sale results from Heritage Place, ranch sales, and Facebook groups.
"""

import re
from typing import List, Dict, Optional
from datetime import date, datetime
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)


@dataclass
class SaleResult:
    """Horse sale result data."""
    sale_name: str
    sale_date: date
    location: str

    # Horse info
    horse_name: str
    hip_number: str = ""
    sex: str = ""  # stallion, mare, gelding
    age: int = 0
    color: str = ""

    # Sale info
    sale_price: float = 0.0
    consignor: str = ""
    buyer: str = ""
    reserve_met: bool = True

    # Pedigree
    sire: str = ""
    dam: str = ""
    dam_sire: str = ""

    # Performance info
    lte: float = 0.0  # Lifetime Tournament Earnings
    ncha_earnings: float = 0.0
    nrcha_earnings: float = 0.0

    # Metadata
    source: str = ""
    listing_url: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "sale_name": self.sale_name,
            "sale_date": self.sale_date.isoformat() if self.sale_date else "",
            "location": self.location,
            "horse_name": self.horse_name,
            "hip_number": self.hip_number,
            "sex": self.sex,
            "age": self.age,
            "color": self.color,
            "sale_price": self.sale_price,
            "consignor": self.consignor,
            "buyer": self.buyer,
            "reserve_met": self.reserve_met,
            "sire": self.sire,
            "dam": self.dam,
            "dam_sire": self.dam_sire,
            "lte": self.lte,
            "ncha_earnings": self.ncha_earnings,
            "nrcha_earnings": self.nrcha_earnings,
            "source": self.source,
            "listing_url": self.listing_url,
            "scraped_at": self.scraped_at.isoformat()
        }


class HorseSaleScraper:
    """Scraper for horse sale results."""

    SALE_SITES = {
        "heritage_place": "https://heritageplace.com",
        "wagonhound": "https://www.wagonhoundranch.com",
        "rocking_p": "https://www.rockingpranch.com",
        "triangle_sales": "https://www.trianglesales.com"
    }

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

    async def scrape_heritage_place(
        self,
        sale_id: str = None,
        year: int = None
    ) -> List[SaleResult]:
        """Scrape Heritage Place sale results."""
        results = []

        if not year:
            year = datetime.now().year

        base_url = self.SALE_SITES["heritage_place"]

        if sale_id:
            url = f"{base_url}/sales/{sale_id}/results"
        else:
            url = f"{base_url}/sales/results?year={year}"

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(url, wait_until='networkidle')
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching Heritage Place: {e}")
            return results

        soup = BeautifulSoup(html, 'html.parser')

        sale_rows = soup.select('.sale-result, .horse-row, tr.result')
        current_sale = ""

        for row in sale_rows:
            try:
                # Check for sale header
                sale_header = row.select_one('.sale-name')
                if sale_header:
                    current_sale = sale_header.get_text(strip=True)
                    continue

                cells = row.select('td')
                if len(cells) < 4:
                    continue

                hip = cells[0].get_text(strip=True) if cells else ""
                horse_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                price_str = cells[2].get_text(strip=True) if len(cells) > 2 else "0"

                # Parse price
                price = float(re.sub(r'[^\d.]', '', price_str)) if price_str else 0

                # Sire/Dam if available
                sire = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                dam = cells[4].get_text(strip=True) if len(cells) > 4 else ""

                # Buyer/Consignor
                consignor = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                buyer = cells[6].get_text(strip=True) if len(cells) > 6 else ""

                results.append(SaleResult(
                    sale_name=current_sale or "Heritage Place Sale",
                    sale_date=date.today(),
                    location="Oklahoma City, OK",
                    horse_name=horse_name,
                    hip_number=hip,
                    sale_price=price,
                    sire=sire,
                    dam=dam,
                    consignor=consignor,
                    buyer=buyer,
                    source="heritage_place"
                ))

            except Exception as e:
                logger.error(f"Error parsing sale row: {e}")
                continue

        return results

    async def scrape_ranch_sale(
        self,
        ranch: str,
        sale_url: str = None
    ) -> List[SaleResult]:
        """Scrape ranch production sale results."""
        results = []

        if ranch not in self.SALE_SITES:
            return results

        base_url = self.SALE_SITES[ranch]
        url = sale_url or f"{base_url}/sale-results"

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(url, wait_until='networkidle')
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching {ranch}: {e}")
            return results

        soup = BeautifulSoup(html, 'html.parser')

        # Ranch sites vary in structure, generic parsing
        sale_items = soup.select('.sale-horse, .lot-item, .horse-card')

        for item in sale_items:
            try:
                name_elem = item.select_one('.horse-name, .lot-name, h3')
                price_elem = item.select_one('.price, .sale-price, .sold-for')
                sire_elem = item.select_one('.sire, .by')
                dam_elem = item.select_one('.dam, .out-of')

                results.append(SaleResult(
                    sale_name=f"{ranch.replace('_', ' ').title()} Sale",
                    sale_date=date.today(),
                    location="",
                    horse_name=name_elem.get_text(strip=True) if name_elem else "",
                    sale_price=float(re.sub(r'[^\d.]', '', price_elem.get_text())) if price_elem else 0,
                    sire=sire_elem.get_text(strip=True) if sire_elem else "",
                    dam=dam_elem.get_text(strip=True) if dam_elem else "",
                    source=ranch
                ))

            except Exception as e:
                logger.error(f"Error parsing ranch sale item: {e}")
                continue

        return results

    async def scrape_sale_catalog(self, catalog_url: str) -> List[Dict]:
        """Scrape upcoming sale catalog entries."""
        entries = []

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(catalog_url, wait_until='networkidle')
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching catalog: {e}")
            return entries

        soup = BeautifulSoup(html, 'html.parser')

        catalog_items = soup.select('.catalog-entry, .horse-listing, .lot')

        for item in catalog_items:
            try:
                hip = item.select_one('.hip-number, .lot-number')
                name = item.select_one('.horse-name')
                sire = item.select_one('.sire')
                dam = item.select_one('.dam')
                sex = item.select_one('.sex, .gender')
                color = item.select_one('.color')
                consignor = item.select_one('.consignor')
                desc = item.select_one('.description')

                entries.append({
                    "hip_number": hip.get_text(strip=True) if hip else "",
                    "horse_name": name.get_text(strip=True) if name else "",
                    "sire": sire.get_text(strip=True) if sire else "",
                    "dam": dam.get_text(strip=True) if dam else "",
                    "sex": sex.get_text(strip=True) if sex else "",
                    "color": color.get_text(strip=True) if color else "",
                    "consignor": consignor.get_text(strip=True) if consignor else "",
                    "description": desc.get_text(strip=True)[:500] if desc else ""
                })

            except Exception:
                continue

        return entries

    async def get_recent_sales(self, limit: int = 50) -> List[SaleResult]:
        """Get most recent sale results across all sources."""
        all_results = []

        # Scrape Heritage Place
        heritage = await self.scrape_heritage_place()
        all_results.extend(heritage[:limit // 2])

        # Scrape major ranch sales
        for ranch in ["wagonhound", "rocking_p"]:
            try:
                ranch_results = await self.scrape_ranch_sale(ranch)
                all_results.extend(ranch_results[:limit // 4])
            except Exception:
                continue

        return all_results[:limit]

    def parse_price_from_text(self, text: str) -> float:
        """Extract price from text like 'Sold for $45,000'."""
        match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', text)
        if match:
            return float(match.group(1).replace(',', ''))
        return 0.0
