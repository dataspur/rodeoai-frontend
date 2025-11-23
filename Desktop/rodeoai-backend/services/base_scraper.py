"""
Base Scraper Class
Abstract base class for all scraping implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedPost:
    """Data class for scraped social media posts."""
    platform: str
    post_id: str
    author: str
    author_handle: Optional[str]
    content: str
    timestamp: Optional[datetime]
    likes: int = 0
    comments: int = 0
    shares: int = 0
    media_urls: List[str] = None
    url: Optional[str] = None
    raw_data: Optional[Dict] = None

    def __post_init__(self):
        if self.media_urls is None:
            self.media_urls = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "post_id": self.post_id,
            "author": self.author,
            "author_handle": self.author_handle,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "media_urls": self.media_urls,
            "url": self.url
        }


@dataclass
class ScrapedProfile:
    """Data class for scraped social media profiles."""
    platform: str
    username: str
    display_name: str
    bio: Optional[str]
    followers: int = 0
    following: int = 0
    post_count: int = 0
    profile_image_url: Optional[str] = None
    website: Optional[str] = None
    verified: bool = False
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "username": self.username,
            "display_name": self.display_name,
            "bio": self.bio,
            "followers": self.followers,
            "following": self.following,
            "post_count": self.post_count,
            "profile_image_url": self.profile_image_url,
            "website": self.website,
            "verified": self.verified,
            "url": self.url
        }


class BaseScraper(ABC):
    """Abstract base class for social media scrapers."""

    def __init__(self, platform: str):
        self.platform = platform
        self.logger = logging.getLogger(f"{__name__}.{platform}")

    @abstractmethod
    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """Scrape a user profile."""
        pass

    @abstractmethod
    async def scrape_posts(self, username: str, limit: int = 10) -> List[ScrapedPost]:
        """Scrape posts from a user."""
        pass

    @abstractmethod
    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """Search for posts by keyword/hashtag."""
        pass

    @abstractmethod
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a specific URL."""
        pass

    async def close(self):
        """Cleanup resources. Override in subclasses if needed."""
        pass

    def _sanitize_text(self, text: Optional[str]) -> str:
        """Clean and sanitize scraped text."""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', '')

    def _parse_count(self, count_str: Optional[str]) -> int:
        """Parse engagement counts like '1.2K', '3.4M' etc."""
        if not count_str:
            return 0

        count_str = count_str.strip().upper().replace(',', '')

        try:
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            else:
                return int(float(count_str))
        except (ValueError, TypeError):
            return 0
