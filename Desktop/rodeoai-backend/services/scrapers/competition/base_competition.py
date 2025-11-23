"""
Base Competition Scraper
Foundation for rodeo/horse show competition data scrapers.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)


@dataclass
class CompetitionResult:
    """Single competition result entry."""
    event_name: str
    event_date: date
    location: str

    # Competitor info
    rider_name: str
    horse_name: str
    owner_name: str = ""

    # Results
    score: float = 0.0
    placing: int = 0
    earnings: float = 0.0
    points: float = 0.0

    # Class/Division info
    division: str = ""  # Open, Non-Pro, Amateur, Youth, etc.
    go_round: str = ""  # Go 1, Go 2, Finals, etc.

    # Judges
    judges: List[str] = field(default_factory=list)

    # Metadata
    source: str = ""
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "event_name": self.event_name,
            "event_date": self.event_date.isoformat() if self.event_date else "",
            "location": self.location,
            "rider_name": self.rider_name,
            "horse_name": self.horse_name,
            "owner_name": self.owner_name,
            "score": self.score,
            "placing": self.placing,
            "earnings": self.earnings,
            "points": self.points,
            "division": self.division,
            "go_round": self.go_round,
            "judges": self.judges,
            "source": self.source,
            "scraped_at": self.scraped_at.isoformat()
        }


@dataclass
class Standings:
    """Standings/rankings data."""
    year: int
    division: str
    category: str  # rider, horse, owner

    # Ranking data
    rank: int
    name: str  # rider or horse name
    earnings: float = 0.0
    points: float = 0.0
    shows_entered: int = 0
    wins: int = 0

    # Associated info
    horse_name: str = ""  # if rider standings
    rider_name: str = ""  # if horse standings
    owner_name: str = ""
    trainer_name: str = ""

    # Pedigree (if horse)
    sire: str = ""
    dam: str = ""
    breeder: str = ""

    source: str = ""

    def to_dict(self) -> Dict:
        return {
            "year": self.year,
            "division": self.division,
            "category": self.category,
            "rank": self.rank,
            "name": self.name,
            "earnings": self.earnings,
            "points": self.points,
            "shows_entered": self.shows_entered,
            "wins": self.wins,
            "horse_name": self.horse_name,
            "rider_name": self.rider_name,
            "owner_name": self.owner_name,
            "trainer_name": self.trainer_name,
            "sire": self.sire,
            "dam": self.dam,
            "breeder": self.breeder,
            "source": self.source
        }


@dataclass
class Event:
    """Upcoming or past event data."""
    event_name: str
    start_date: date
    end_date: date
    location: str
    venue: str = ""

    # Event details
    purse: float = 0.0
    entry_fee: float = 0.0
    divisions: List[str] = field(default_factory=list)

    # Entry info
    entries_open: bool = False
    entry_count: int = 0
    entry_deadline: Optional[date] = None

    # URLs
    event_url: str = ""
    results_url: str = ""
    entries_url: str = ""

    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled

    source: str = ""

    def to_dict(self) -> Dict:
        return {
            "event_name": self.event_name,
            "start_date": self.start_date.isoformat() if self.start_date else "",
            "end_date": self.end_date.isoformat() if self.end_date else "",
            "location": self.location,
            "venue": self.venue,
            "purse": self.purse,
            "entry_fee": self.entry_fee,
            "divisions": self.divisions,
            "entries_open": self.entries_open,
            "entry_count": self.entry_count,
            "entry_deadline": self.entry_deadline.isoformat() if self.entry_deadline else "",
            "event_url": self.event_url,
            "results_url": self.results_url,
            "entries_url": self.entries_url,
            "status": self.status,
            "source": self.source
        }


class BaseCompetitionScraper(ABC):
    """Base class for competition data scrapers."""

    ASSOCIATION = "base"
    BASE_URL = ""

    DIVISIONS = []

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

    async def close(self):
        if self.browser:
            await self.browser.close()

    @abstractmethod
    async def scrape_results(
        self,
        event_id: str = None,
        year: int = None,
        division: str = None
    ) -> List[CompetitionResult]:
        """Scrape competition results."""
        pass

    @abstractmethod
    async def scrape_standings(
        self,
        year: int,
        division: str,
        category: str = "rider"
    ) -> List[Standings]:
        """Scrape current standings."""
        pass

    @abstractmethod
    async def scrape_events(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> List[Event]:
        """Scrape upcoming/past events."""
        pass

    @abstractmethod
    async def scrape_entries(self, event_id: str) -> List[Dict]:
        """Scrape entry list for an event."""
        pass

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

    def parse_money(self, money_str: str) -> float:
        """Parse money string to float."""
        if not money_str:
            return 0.0
        import re
        cleaned = re.sub(r'[^\d.]', '', money_str)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        from dateutil import parser
        try:
            return parser.parse(date_str).date()
        except Exception:
            return None
