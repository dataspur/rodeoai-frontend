"""
NCHA Scraper
Scrapes nchacutting.com for cutting horse competition data.
"""

import re
from typing import List, Dict, Optional
from datetime import date, datetime
from bs4 import BeautifulSoup
from .base_competition import BaseCompetitionScraper, CompetitionResult, Standings, Event
import logging

logger = logging.getLogger(__name__)


class NCHAScraper(BaseCompetitionScraper):
    """Scraper for NCHA (National Cutting Horse Association)"""

    ASSOCIATION = "ncha"
    BASE_URL = "https://www.nchacutting.com"

    DIVISIONS = [
        "open", "non_pro", "amateur", "youth",
        "50_amateur", "35_non_pro", "25_non_pro",
        "15_amateur", "5000_novice_horse", "2500_novice_horse",
        "1000_novice_rider", "limited_non_pro"
    ]

    MAJOR_EVENTS = [
        "futurity", "super_stakes", "summer_spectacular",
        "world_championship_futurity", "western_nationals"
    ]

    async def scrape_results(
        self,
        event_id: str = None,
        year: int = None,
        division: str = None
    ) -> List[CompetitionResult]:
        """Scrape NCHA competition results."""
        results = []

        if not year:
            year = datetime.now().year

        # Build URL based on parameters
        if event_id:
            url = f"{self.BASE_URL}/shows/{event_id}/results"
        else:
            url = f"{self.BASE_URL}/shows/results?year={year}"
            if division:
                url += f"&division={division}"

        html = await self.get_page_content(url)
        if not html:
            return results

        soup = BeautifulSoup(html, 'html.parser')

        # Parse results table
        result_rows = soup.select('.results-table tr, .show-results tr')

        current_event = ""
        current_division = ""
        current_date = None

        for row in result_rows:
            try:
                # Check for event header
                event_header = row.select_one('.event-name, .show-name')
                if event_header:
                    current_event = event_header.get_text(strip=True)
                    continue

                # Check for division header
                div_header = row.select_one('.division-name, .class-name')
                if div_header:
                    current_division = div_header.get_text(strip=True)
                    continue

                # Parse result row
                cells = row.select('td')
                if len(cells) < 4:
                    continue

                placing = int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else 0
                rider = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                horse = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                score = float(cells[3].get_text(strip=True)) if len(cells) > 3 else 0.0

                # Optional fields
                earnings = self.parse_money(cells[4].get_text()) if len(cells) > 4 else 0.0
                owner = cells[5].get_text(strip=True) if len(cells) > 5 else ""

                results.append(CompetitionResult(
                    event_name=current_event,
                    event_date=current_date or date.today(),
                    location="",
                    rider_name=rider,
                    horse_name=horse,
                    owner_name=owner,
                    score=score,
                    placing=placing,
                    earnings=earnings,
                    division=current_division or division or "",
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing result row: {e}")
                continue

        return results

    async def scrape_standings(
        self,
        year: int,
        division: str,
        category: str = "rider"
    ) -> List[Standings]:
        """Scrape NCHA standings."""
        standings = []

        url = f"{self.BASE_URL}/standings/{year}/{division}"
        if category == "horse":
            url += "/horses"

        html = await self.get_page_content(url)
        if not html:
            return standings

        soup = BeautifulSoup(html, 'html.parser')

        standings_rows = soup.select('.standings-table tr, .rankings-row')

        for row in standings_rows:
            try:
                cells = row.select('td')
                if len(cells) < 3:
                    continue

                rank = int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else 0
                name = cells[1].get_text(strip=True)
                earnings = self.parse_money(cells[2].get_text()) if len(cells) > 2 else 0.0

                # Additional fields
                points = float(cells[3].get_text(strip=True)) if len(cells) > 3 else 0.0
                shows = int(cells[4].get_text(strip=True)) if len(cells) > 4 and cells[4].get_text(strip=True).isdigit() else 0

                # Horse/rider association
                associated_name = cells[5].get_text(strip=True) if len(cells) > 5 else ""

                standings.append(Standings(
                    year=year,
                    division=division,
                    category=category,
                    rank=rank,
                    name=name,
                    earnings=earnings,
                    points=points,
                    shows_entered=shows,
                    horse_name=associated_name if category == "rider" else name,
                    rider_name=associated_name if category == "horse" else name,
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing standings row: {e}")
                continue

        return standings

    async def scrape_events(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> List[Event]:
        """Scrape NCHA events calendar."""
        events = []

        url = f"{self.BASE_URL}/events"
        if start_date:
            url += f"?start={start_date.isoformat()}"
        if end_date:
            url += f"&end={end_date.isoformat()}"

        html = await self.get_page_content(url)
        if not html:
            return events

        soup = BeautifulSoup(html, 'html.parser')

        event_cards = soup.select('.event-card, .show-listing, .calendar-event')

        for card in event_cards:
            try:
                name_elem = card.select_one('.event-name, .show-name, h3')
                name = name_elem.get_text(strip=True) if name_elem else ""

                date_elem = card.select_one('.event-date, .show-date')
                date_str = date_elem.get_text(strip=True) if date_elem else ""

                location_elem = card.select_one('.event-location, .show-location')
                location = location_elem.get_text(strip=True) if location_elem else ""

                venue_elem = card.select_one('.venue-name')
                venue = venue_elem.get_text(strip=True) if venue_elem else ""

                purse_elem = card.select_one('.purse-amount, .added-money')
                purse = self.parse_money(purse_elem.get_text()) if purse_elem else 0.0

                link = card.select_one('a[href]')
                event_url = link.get('href') if link else ""

                # Parse date range
                parsed_start = self.parse_date(date_str.split('-')[0].strip())
                parsed_end = self.parse_date(date_str.split('-')[-1].strip()) if '-' in date_str else parsed_start

                events.append(Event(
                    event_name=name,
                    start_date=parsed_start or date.today(),
                    end_date=parsed_end or date.today(),
                    location=location,
                    venue=venue,
                    purse=purse,
                    event_url=event_url if event_url.startswith('http') else self.BASE_URL + event_url,
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing event: {e}")
                continue

        return events

    async def scrape_entries(self, event_id: str) -> List[Dict]:
        """Scrape entry list for NCHA event."""
        entries = []

        url = f"{self.BASE_URL}/shows/{event_id}/entries"
        html = await self.get_page_content(url)
        if not html:
            return entries

        soup = BeautifulSoup(html, 'html.parser')

        entry_rows = soup.select('.entry-row, .entries-table tr')

        for row in entry_rows:
            try:
                cells = row.select('td')
                if len(cells) < 3:
                    continue

                entries.append({
                    "entry_number": cells[0].get_text(strip=True) if len(cells) > 0 else "",
                    "rider_name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                    "horse_name": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    "owner_name": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                    "division": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                    "draw_position": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                    "set_number": cells[6].get_text(strip=True) if len(cells) > 6 else ""
                })

            except Exception as e:
                logger.error(f"Error parsing entry: {e}")
                continue

        return entries

    async def scrape_futurity_results(self, year: int = None) -> List[CompetitionResult]:
        """Scrape NCHA Futurity results specifically."""
        if not year:
            year = datetime.now().year

        url = f"{self.BASE_URL}/shows/futurity/{year}/results"
        return await self._scrape_major_event_results(url, "NCHA Futurity", year)

    async def scrape_futurity_entries(self, year: int = None) -> List[Dict]:
        """Scrape NCHA Futurity entry verification."""
        if not year:
            year = datetime.now().year

        url = f"{self.BASE_URL}/shows/futurity/futurity-entry-verification"
        html = await self.get_page_content(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        entries = []

        entry_rows = soup.select('.entry-verification tr, .futurity-entry')

        for row in entry_rows:
            try:
                cells = row.select('td')
                if len(cells) < 2:
                    continue

                entries.append({
                    "horse_name": cells[0].get_text(strip=True) if cells else "",
                    "rider_name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                    "owner_name": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    "trainer_name": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                    "division": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                    "sire": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                    "dam": cells[6].get_text(strip=True) if len(cells) > 6 else ""
                })

            except Exception:
                continue

        return entries

    async def _scrape_major_event_results(
        self,
        url: str,
        event_name: str,
        year: int
    ) -> List[CompetitionResult]:
        """Helper to scrape major event results."""
        results = []

        html = await self.get_page_content(url)
        if not html:
            return results

        soup = BeautifulSoup(html, 'html.parser')
        result_rows = soup.select('.results-table tr')

        current_division = ""
        current_round = ""

        for row in result_rows:
            try:
                # Check for division/round headers
                header = row.select_one('.division-header, .round-header')
                if header:
                    text = header.get_text(strip=True)
                    if "go" in text.lower() or "final" in text.lower():
                        current_round = text
                    else:
                        current_division = text
                    continue

                cells = row.select('td')
                if len(cells) < 4:
                    continue

                results.append(CompetitionResult(
                    event_name=f"{event_name} {year}",
                    event_date=date(year, 12, 1),  # Futurity is typically in December
                    location="Fort Worth, TX",
                    rider_name=cells[1].get_text(strip=True) if len(cells) > 1 else "",
                    horse_name=cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    score=float(cells[3].get_text(strip=True)) if len(cells) > 3 else 0.0,
                    placing=int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else 0,
                    earnings=self.parse_money(cells[4].get_text()) if len(cells) > 4 else 0.0,
                    division=current_division,
                    go_round=current_round,
                    source=self.ASSOCIATION
                ))

            except Exception as e:
                logger.error(f"Error parsing major event result: {e}")
                continue

        return results

    async def search_rider(self, name: str) -> List[Dict]:
        """Search for a rider's records."""
        url = f"{self.BASE_URL}/members/search?q={name.replace(' ', '+')}"
        html = await self.get_page_content(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        results = []

        member_cards = soup.select('.member-card, .search-result')

        for card in member_cards:
            try:
                name_elem = card.select_one('.member-name')
                earnings_elem = card.select_one('.lifetime-earnings')
                link = card.select_one('a[href]')

                results.append({
                    "name": name_elem.get_text(strip=True) if name_elem else "",
                    "lifetime_earnings": self.parse_money(earnings_elem.get_text()) if earnings_elem else 0,
                    "profile_url": link.get('href') if link else ""
                })
            except Exception:
                continue

        return results

    async def search_horse(self, name: str) -> List[Dict]:
        """Search for a horse's records."""
        url = f"{self.BASE_URL}/horses/search?q={name.replace(' ', '+')}"
        html = await self.get_page_content(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        results = []

        horse_cards = soup.select('.horse-card, .search-result')

        for card in horse_cards:
            try:
                name_elem = card.select_one('.horse-name')
                sire_elem = card.select_one('.sire')
                dam_elem = card.select_one('.dam')
                earnings_elem = card.select_one('.earnings')

                results.append({
                    "name": name_elem.get_text(strip=True) if name_elem else "",
                    "sire": sire_elem.get_text(strip=True) if sire_elem else "",
                    "dam": dam_elem.get_text(strip=True) if dam_elem else "",
                    "lifetime_earnings": self.parse_money(earnings_elem.get_text()) if earnings_elem else 0
                })
            except Exception:
                continue

        return results
