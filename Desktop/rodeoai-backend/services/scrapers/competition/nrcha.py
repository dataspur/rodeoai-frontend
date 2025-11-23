"""
NRCHA Scraper
Scrapes nrcha.com for reining cow horse competition data.
"""

from typing import List, Dict, Optional
from datetime import date, datetime
from bs4 import BeautifulSoup
from .base_competition import BaseCompetitionScraper, CompetitionResult, Standings, Event
import logging

logger = logging.getLogger(__name__)


class NRCHAScraper(BaseCompetitionScraper):
    """Scraper for NRCHA (National Reined Cow Horse Association)"""

    ASSOCIATION = "nrcha"
    BASE_URL = "https://www.nrcha.com"

    DIVISIONS = [
        "open", "intermediate_open", "limited_open",
        "non_pro", "intermediate_non_pro", "limited_non_pro",
        "youth", "rookie"
    ]

    DISCIPLINES = [
        "bridle", "hackamore", "two_rein", "snaffle_bit"
    ]

    async def scrape_results(
        self,
        event_id: str = None,
        year: int = None,
        division: str = None
    ) -> List[CompetitionResult]:
        """Scrape NRCHA competition results."""
        results = []

        if not year:
            year = datetime.now().year

        if event_id:
            url = f"{self.BASE_URL}/events/{event_id}/results"
        else:
            url = f"{self.BASE_URL}/results?year={year}"
            if division:
                url += f"&class={division}"

        html = await self.get_page_content(url)
        if not html:
            return results

        soup = BeautifulSoup(html, 'html.parser')
        result_rows = soup.select('.results-row, .show-result tr')

        current_event = ""
        current_division = ""

        for row in result_rows:
            try:
                event_header = row.select_one('.event-title')
                if event_header:
                    current_event = event_header.get_text(strip=True)
                    continue

                div_header = row.select_one('.class-title')
                if div_header:
                    current_division = div_header.get_text(strip=True)
                    continue

                cells = row.select('td')
                if len(cells) < 4:
                    continue

                # NRCHA results typically include composite scores
                # (herd work + rein work + cow work)
                placing = int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else 0
                rider = cells[1].get_text(strip=True)
                horse = cells[2].get_text(strip=True)

                # Composite score
                score = float(cells[3].get_text(strip=True)) if len(cells) > 3 else 0.0

                # Individual scores if available
                herd_score = float(cells[4].get_text(strip=True)) if len(cells) > 4 else 0.0
                rein_score = float(cells[5].get_text(strip=True)) if len(cells) > 5 else 0.0
                cow_score = float(cells[6].get_text(strip=True)) if len(cells) > 6 else 0.0

                earnings = self.parse_money(cells[7].get_text()) if len(cells) > 7 else 0.0

                results.append(CompetitionResult(
                    event_name=current_event,
                    event_date=date.today(),
                    location="",
                    rider_name=rider,
                    horse_name=horse,
                    score=score,
                    placing=placing,
                    earnings=earnings,
                    division=current_division or division or "",
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing NRCHA result: {e}")
                continue

        return results

    async def scrape_standings(
        self,
        year: int,
        division: str,
        category: str = "rider"
    ) -> List[Standings]:
        """Scrape NRCHA standings."""
        standings = []

        url = f"{self.BASE_URL}/standings/{year}/{division}"
        html = await self.get_page_content(url)
        if not html:
            return standings

        soup = BeautifulSoup(html, 'html.parser')
        standings_rows = soup.select('.standings-row, .ranking-entry')

        for row in standings_rows:
            try:
                cells = row.select('td')
                if len(cells) < 3:
                    continue

                rank = int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else 0
                name = cells[1].get_text(strip=True)
                earnings = self.parse_money(cells[2].get_text())

                standings.append(Standings(
                    year=year,
                    division=division,
                    category=category,
                    rank=rank,
                    name=name,
                    earnings=earnings,
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing standings: {e}")
                continue

        return standings

    async def scrape_events(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> List[Event]:
        """Scrape NRCHA events."""
        events = []

        url = f"{self.BASE_URL}/events"
        html = await self.get_page_content(url)
        if not html:
            return events

        soup = BeautifulSoup(html, 'html.parser')
        event_items = soup.select('.event-item, .show-card')

        for item in event_items:
            try:
                name = item.select_one('.event-name, .show-title')
                date_elem = item.select_one('.event-date')
                location = item.select_one('.event-location')
                link = item.select_one('a[href]')

                parsed_date = self.parse_date(date_elem.get_text() if date_elem else "")

                events.append(Event(
                    event_name=name.get_text(strip=True) if name else "",
                    start_date=parsed_date or date.today(),
                    end_date=parsed_date or date.today(),
                    location=location.get_text(strip=True) if location else "",
                    event_url=link.get('href') if link else "",
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing event: {e}")
                continue

        return events

    async def scrape_entries(self, event_id: str) -> List[Dict]:
        """Scrape NRCHA event entries."""
        entries = []

        url = f"{self.BASE_URL}/events/{event_id}/entries"
        html = await self.get_page_content(url)
        if not html:
            return entries

        soup = BeautifulSoup(html, 'html.parser')
        entry_rows = soup.select('.entry-row, .entries tr')

        for row in entry_rows:
            try:
                cells = row.select('td')
                if len(cells) < 2:
                    continue

                entries.append({
                    "rider_name": cells[0].get_text(strip=True),
                    "horse_name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                    "division": cells[2].get_text(strip=True) if len(cells) > 2 else ""
                })
            except Exception:
                continue

        return entries

    async def scrape_snaffle_bit_futurity(self, year: int = None) -> List[CompetitionResult]:
        """Scrape NRCHA Snaffle Bit Futurity results."""
        if not year:
            year = datetime.now().year

        url = f"{self.BASE_URL}/events/snaffle-bit-futurity/{year}/results"
        html = await self.get_page_content(url)
        if not html:
            return []

        results = []
        soup = BeautifulSoup(html, 'html.parser')

        result_rows = soup.select('.futurity-results tr')
        current_div = ""

        for row in result_rows:
            try:
                header = row.select_one('.division-header')
                if header:
                    current_div = header.get_text(strip=True)
                    continue

                cells = row.select('td')
                if len(cells) < 4:
                    continue

                results.append(CompetitionResult(
                    event_name=f"NRCHA Snaffle Bit Futurity {year}",
                    event_date=date(year, 10, 1),
                    location="Reno, NV",
                    rider_name=cells[1].get_text(strip=True),
                    horse_name=cells[2].get_text(strip=True),
                    score=float(cells[3].get_text(strip=True)) if cells[3].get_text(strip=True) else 0,
                    placing=int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else 0,
                    earnings=self.parse_money(cells[4].get_text()) if len(cells) > 4 else 0,
                    division=current_div,
                    source=self.ASSOCIATION
                ))
            except Exception:
                continue

        return results
