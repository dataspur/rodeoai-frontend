"""
Pedigree Scrapers
Scrapes pedigree data from AllBreedPedigree, AQHA, and other sources.
"""

from typing import List, Dict, Optional
from datetime import date
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)


@dataclass
class HorsePedigree:
    """Complete pedigree data for a horse."""
    horse_name: str
    registration_number: str = ""
    breed: str = "Quarter Horse"

    # Basic info
    sex: str = ""
    color: str = ""
    foal_date: Optional[date] = None
    breeder: str = ""

    # Sire line
    sire: str = ""
    sire_sire: str = ""
    sire_dam: str = ""
    sire_sire_sire: str = ""
    sire_sire_dam: str = ""
    sire_dam_sire: str = ""
    sire_dam_dam: str = ""

    # Dam line
    dam: str = ""
    dam_sire: str = ""
    dam_dam: str = ""
    dam_sire_sire: str = ""
    dam_sire_dam: str = ""
    dam_dam_sire: str = ""
    dam_dam_dam: str = ""

    # Performance
    ncha_earnings: float = 0.0
    nrcha_earnings: float = 0.0
    nrha_earnings: float = 0.0
    aqha_points: int = 0

    # Offspring stats
    offspring_count: int = 0
    offspring_earnings: float = 0.0

    # Source
    source: str = ""
    source_url: str = ""

    def to_dict(self) -> Dict:
        return {
            "horse_name": self.horse_name,
            "registration_number": self.registration_number,
            "breed": self.breed,
            "sex": self.sex,
            "color": self.color,
            "foal_date": self.foal_date.isoformat() if self.foal_date else "",
            "breeder": self.breeder,
            "pedigree": {
                "sire": {
                    "name": self.sire,
                    "sire": self.sire_sire,
                    "dam": self.sire_dam,
                    "sire_sire": self.sire_sire_sire,
                    "sire_dam": self.sire_sire_dam,
                    "dam_sire": self.sire_dam_sire,
                    "dam_dam": self.sire_dam_dam
                },
                "dam": {
                    "name": self.dam,
                    "sire": self.dam_sire,
                    "dam": self.dam_dam,
                    "sire_sire": self.dam_sire_sire,
                    "sire_dam": self.dam_sire_dam,
                    "dam_sire": self.dam_dam_sire,
                    "dam_dam": self.dam_dam_dam
                }
            },
            "performance": {
                "ncha_earnings": self.ncha_earnings,
                "nrcha_earnings": self.nrcha_earnings,
                "nrha_earnings": self.nrha_earnings,
                "aqha_points": self.aqha_points
            },
            "offspring": {
                "count": self.offspring_count,
                "total_earnings": self.offspring_earnings
            },
            "source": self.source,
            "source_url": self.source_url
        }

    def get_full_pedigree(self, generations: int = 4) -> Dict:
        """Get pedigree as nested structure."""
        return {
            "name": self.horse_name,
            "sire": {
                "name": self.sire,
                "sire": {"name": self.sire_sire},
                "dam": {"name": self.sire_dam}
            },
            "dam": {
                "name": self.dam,
                "sire": {"name": self.dam_sire},
                "dam": {"name": self.dam_dam}
            }
        }


class PedigreeScraper:
    """Scraper for horse pedigree data."""

    SOURCES = {
        "allbreedpedigree": "https://www.allbreedpedigree.com",
        "aqha": "https://www.aqha.com",
        "equineregistry": "https://www.equineregistry.com"
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

    async def search_horse(self, name: str) -> List[Dict]:
        """Search for a horse across pedigree databases."""
        results = []

        # Search AllBreedPedigree
        abp_results = await self._search_allbreedpedigree(name)
        results.extend(abp_results)

        return results

    async def _search_allbreedpedigree(self, name: str) -> List[Dict]:
        """Search AllBreedPedigree.com"""
        results = []

        url = f"{self.SOURCES['allbreedpedigree']}/search?query={name.replace(' ', '+')}"

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(url, wait_until='networkidle')
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error searching AllBreedPedigree: {e}")
            return results

        soup = BeautifulSoup(html, 'html.parser')

        search_results = soup.select('.search-result, .horse-result, tr.result')

        for result in search_results[:20]:
            try:
                name_elem = result.select_one('.horse-name, a')
                sire_elem = result.select_one('.sire')
                dam_elem = result.select_one('.dam')
                link = result.select_one('a[href]')

                results.append({
                    "name": name_elem.get_text(strip=True) if name_elem else "",
                    "sire": sire_elem.get_text(strip=True) if sire_elem else "",
                    "dam": dam_elem.get_text(strip=True) if dam_elem else "",
                    "url": link.get('href') if link else "",
                    "source": "allbreedpedigree"
                })
            except Exception:
                continue

        return results

    async def get_pedigree(self, horse_name: str, source: str = "allbreedpedigree") -> Optional[HorsePedigree]:
        """Get full pedigree for a horse."""
        if source == "allbreedpedigree":
            return await self._get_allbreedpedigree(horse_name)
        return None

    async def _get_allbreedpedigree(self, horse_name: str) -> Optional[HorsePedigree]:
        """Get pedigree from AllBreedPedigree.com"""
        # First search for the horse
        search_results = await self._search_allbreedpedigree(horse_name)
        if not search_results:
            return None

        # Get the first result's URL
        horse_url = search_results[0].get("url", "")
        if not horse_url:
            return None

        if not horse_url.startswith("http"):
            horse_url = self.SOURCES["allbreedpedigree"] + horse_url

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(horse_url, wait_until='networkidle')
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching pedigree: {e}")
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Parse pedigree table
            pedigree_table = soup.select_one('.pedigree-table, #pedigree')

            if not pedigree_table:
                return None

            # Extract horse info
            name_elem = soup.select_one('h1, .horse-name')
            name = name_elem.get_text(strip=True) if name_elem else horse_name

            # Parse pedigree cells - structure varies
            cells = pedigree_table.select('td, .pedigree-cell')

            # Typical 5-generation pedigree layout
            sire = ""
            dam = ""
            sire_sire = ""
            sire_dam = ""
            dam_sire = ""
            dam_dam = ""

            if len(cells) >= 2:
                sire = cells[0].get_text(strip=True) if cells[0] else ""
                dam = cells[1].get_text(strip=True) if len(cells) > 1 else ""

            if len(cells) >= 6:
                sire_sire = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                sire_dam = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                dam_sire = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                dam_dam = cells[5].get_text(strip=True) if len(cells) > 5 else ""

            # Get additional info
            reg_elem = soup.select_one('.registration-number, .reg-num')
            color_elem = soup.select_one('.color')
            sex_elem = soup.select_one('.sex, .gender')
            breeder_elem = soup.select_one('.breeder')

            return HorsePedigree(
                horse_name=name,
                registration_number=reg_elem.get_text(strip=True) if reg_elem else "",
                sex=sex_elem.get_text(strip=True) if sex_elem else "",
                color=color_elem.get_text(strip=True) if color_elem else "",
                breeder=breeder_elem.get_text(strip=True) if breeder_elem else "",
                sire=sire,
                dam=dam,
                sire_sire=sire_sire,
                sire_dam=sire_dam,
                dam_sire=dam_sire,
                dam_dam=dam_dam,
                source="allbreedpedigree",
                source_url=horse_url
            )

        except Exception as e:
            logger.error(f"Error parsing pedigree: {e}")
            return None

    async def get_offspring(self, horse_name: str, limit: int = 50) -> List[Dict]:
        """Get offspring records for a horse."""
        offspring = []

        # Search for offspring on AllBreedPedigree
        search_results = await self._search_allbreedpedigree(horse_name)
        if not search_results:
            return offspring

        horse_url = search_results[0].get("url", "")
        if not horse_url:
            return offspring

        if not horse_url.startswith("http"):
            horse_url = self.SOURCES["allbreedpedigree"] + horse_url

        offspring_url = horse_url + "/offspring"

        if not self.page:
            await self.init_browser()

        try:
            await self.page.goto(offspring_url, wait_until='networkidle')
            html = await self.page.content()
        except Exception as e:
            logger.error(f"Error fetching offspring: {e}")
            return offspring

        soup = BeautifulSoup(html, 'html.parser')

        offspring_rows = soup.select('.offspring-row, .foal-entry, tr')[:limit]

        for row in offspring_rows:
            try:
                cells = row.select('td')
                if len(cells) < 2:
                    continue

                offspring.append({
                    "name": cells[0].get_text(strip=True) if cells else "",
                    "year": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                    "dam": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    "sex": cells[3].get_text(strip=True) if len(cells) > 3 else ""
                })
            except Exception:
                continue

        return offspring

    async def get_siblings(self, horse_name: str) -> List[Dict]:
        """Get siblings (same dam) for a horse."""
        # First get the horse's dam
        pedigree = await self.get_pedigree(horse_name)
        if not pedigree or not pedigree.dam:
            return []

        # Search for offspring of the dam
        return await self.get_offspring(pedigree.dam, limit=30)
