"""
Deep Scraper Module
Enhanced scrapers with pagination for 100x more data extraction.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..base_scraper import ScrapedPost, ScrapedProfile

logger = logging.getLogger(__name__)


class DeepRedditScraper:
    """
    Enhanced Reddit scraper with deep pagination.
    Can fetch thousands of posts from users and subreddits.
    """

    BASE_URL = "https://www.reddit.com"

    def __init__(self):
        self.headers = {
            "User-Agent": "RodeoAI/2.0 (High-Volume Scraper)"
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def scrape_user_posts_deep(
        self,
        username: str,
        limit: int = 1000,
        sort: str = "new"
    ) -> List[ScrapedPost]:
        """
        Scrape up to 1000 posts from a Reddit user using pagination.

        Args:
            username: Reddit username
            limit: Maximum posts (up to 1000)
            sort: Sort method (new, hot, top)
        """
        posts = []
        after = None
        fetched = 0
        max_per_request = 100

        session = await self._get_session()

        while fetched < limit:
            url = f"{self.BASE_URL}/user/{username}/submitted.json"
            params = {
                "limit": min(max_per_request, limit - fetched),
                "sort": sort
            }
            if after:
                params["after"] = after

            try:
                async with session.get(url, params=params, timeout=30) as resp:
                    if resp.status != 200:
                        logger.warning(f"Reddit returned {resp.status} for user {username}")
                        break

                    data = await resp.json()
                    children = data.get("data", {}).get("children", [])

                    if not children:
                        break

                    for child in children:
                        post_data = child.get("data", {})
                        posts.append(self._parse_post(post_data, username))

                    fetched += len(children)
                    after = data.get("data", {}).get("after")

                    if not after:
                        break

                    # Small delay to avoid rate limits
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching posts for {username}: {e}")
                break

        logger.info(f"Scraped {len(posts)} posts from u/{username}")
        return posts[:limit]

    async def scrape_subreddit_deep(
        self,
        subreddit: str,
        limit: int = 1000,
        sort: str = "hot",
        time_filter: str = "all"
    ) -> List[ScrapedPost]:
        """
        Scrape up to 1000 posts from a subreddit.

        Args:
            subreddit: Subreddit name
            limit: Maximum posts (up to 1000)
            sort: hot, new, top, rising
            time_filter: hour, day, week, month, year, all (for top/controversial)
        """
        posts = []
        after = None
        fetched = 0
        max_per_request = 100

        session = await self._get_session()

        while fetched < limit:
            url = f"{self.BASE_URL}/r/{subreddit}/{sort}.json"
            params = {
                "limit": min(max_per_request, limit - fetched),
                "t": time_filter
            }
            if after:
                params["after"] = after

            try:
                async with session.get(url, params=params, timeout=30) as resp:
                    if resp.status != 200:
                        break

                    data = await resp.json()
                    children = data.get("data", {}).get("children", [])

                    if not children:
                        break

                    for child in children:
                        post_data = child.get("data", {})
                        posts.append(self._parse_post(post_data))

                    fetched += len(children)
                    after = data.get("data", {}).get("after")

                    if not after:
                        break

                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching r/{subreddit}: {e}")
                break

        logger.info(f"Scraped {len(posts)} posts from r/{subreddit}")
        return posts[:limit]

    async def search_deep(
        self,
        query: str,
        limit: int = 1000,
        sort: str = "relevance",
        time_filter: str = "all",
        subreddit: str = None
    ) -> List[ScrapedPost]:
        """
        Deep search Reddit for posts.

        Args:
            query: Search query
            limit: Maximum results
            sort: relevance, hot, top, new, comments
            time_filter: hour, day, week, month, year, all
            subreddit: Optional subreddit to search within
        """
        posts = []
        after = None
        fetched = 0
        max_per_request = 100

        session = await self._get_session()

        base_url = f"{self.BASE_URL}/r/{subreddit}/search.json" if subreddit else f"{self.BASE_URL}/search.json"

        while fetched < limit:
            params = {
                "q": query,
                "limit": min(max_per_request, limit - fetched),
                "sort": sort,
                "t": time_filter,
                "type": "link"
            }
            if subreddit:
                params["restrict_sr"] = "1"
            if after:
                params["after"] = after

            try:
                async with session.get(base_url, params=params, timeout=30) as resp:
                    if resp.status != 200:
                        break

                    data = await resp.json()
                    children = data.get("data", {}).get("children", [])

                    if not children:
                        break

                    for child in children:
                        post_data = child.get("data", {})
                        posts.append(self._parse_post(post_data))

                    fetched += len(children)
                    after = data.get("data", {}).get("after")

                    if not after:
                        break

                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error searching Reddit: {e}")
                break

        logger.info(f"Search found {len(posts)} posts for '{query}'")
        return posts[:limit]

    async def scrape_multiple_subreddits(
        self,
        subreddits: List[str],
        posts_per_sub: int = 100,
        sort: str = "hot"
    ) -> Dict[str, List[ScrapedPost]]:
        """
        Scrape multiple subreddits concurrently.
        """
        results = {}

        async def scrape_one(sub: str):
            posts = await self.scrape_subreddit_deep(sub, posts_per_sub, sort)
            return sub, posts

        tasks = [scrape_one(sub) for sub in subreddits]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, Exception):
                continue
            sub, posts = result
            results[sub] = posts

        total = sum(len(p) for p in results.values())
        logger.info(f"Scraped {total} total posts from {len(results)} subreddits")

        return results

    def _parse_post(self, data: Dict, author: str = None) -> ScrapedPost:
        """Parse Reddit post data into ScrapedPost."""
        timestamp = None
        if data.get("created_utc"):
            timestamp = datetime.utcfromtimestamp(data["created_utc"])

        media_urls = []
        if data.get("url") and any(ext in data["url"].lower() for ext in [".jpg", ".png", ".gif", ".webp"]):
            media_urls.append(data["url"])
        if data.get("thumbnail") and data["thumbnail"].startswith("http"):
            media_urls.append(data["thumbnail"])

        return ScrapedPost(
            platform="reddit",
            post_id=data.get("id", ""),
            author=author or data.get("author", "[deleted]"),
            author_handle=f"u/{author or data.get('author', '[deleted]')}",
            content=f"{data.get('title', '')}\n\n{data.get('selftext', '')}".strip(),
            timestamp=timestamp,
            likes=data.get("ups", 0),
            comments=data.get("num_comments", 0),
            shares=0,
            media_urls=media_urls,
            url=f"https://reddit.com{data.get('permalink', '')}",
            raw_data={
                "subreddit": data.get("subreddit"),
                "score": data.get("score"),
                "upvote_ratio": data.get("upvote_ratio"),
                "flair": data.get("link_flair_text"),
                "is_video": data.get("is_video"),
                "domain": data.get("domain")
            }
        )


class DeepYouTubeScraper:
    """
    Enhanced YouTube scraper using public API endpoints.
    Can fetch more video data through pagination.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_deep(
        self,
        query: str,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Deep search YouTube (requires Playwright for pagination).
        Returns basic video info from search.
        """
        # For deep YouTube scraping, we'd need to use the YouTube Data API
        # or Playwright for scrolling. This is a placeholder.
        from ..scrapers.youtube_scraper import YouTubeScraper

        scraper = YouTubeScraper()
        try:
            # Use standard search but request more
            results = await scraper.search_posts(query, min(limit, 100))
            return [r.to_dict() for r in results]
        finally:
            await scraper.close()


class BulkTwitterScraper:
    """
    Bulk Twitter/X scraper for mass data collection.
    Uses Playwright with session management.
    """

    def __init__(self):
        from ..playwright_scraper import PlaywrightScraper
        self._scraper = PlaywrightScraper(browser_type="chromium", headless=True)

    async def close(self):
        await self._scraper.close()

    async def scrape_multiple_profiles(
        self,
        usernames: List[str],
        concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Scrape multiple Twitter profiles concurrently.
        """
        from ..scrapers.twitter_scraper import TwitterScraper

        results = {}
        semaphore = asyncio.Semaphore(concurrent)

        async def scrape_one(username: str):
            async with semaphore:
                scraper = TwitterScraper()
                try:
                    profile = await scraper.scrape_profile(username)
                    return username, profile.to_dict() if profile else None
                except Exception as e:
                    return username, {"error": str(e)}
                finally:
                    await scraper.close()

        tasks = [scrape_one(u) for u in usernames]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, Exception):
                continue
            username, data = result
            results[username] = data

        return results

    async def scrape_multiple_timelines(
        self,
        usernames: List[str],
        tweets_per_user: int = 50,
        concurrent: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Scrape tweets from multiple users concurrently.
        """
        from ..scrapers.twitter_scraper import TwitterScraper

        results = {}
        semaphore = asyncio.Semaphore(concurrent)

        async def scrape_one(username: str):
            async with semaphore:
                scraper = TwitterScraper()
                try:
                    tweets = await scraper.scrape_posts(username, tweets_per_user)
                    return username, [t.to_dict() for t in tweets]
                except Exception as e:
                    return username, {"error": str(e)}
                finally:
                    await scraper.close()

        tasks = [scrape_one(u) for u in usernames]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, Exception):
                continue
            username, data = result
            results[username] = data

        return results


# Factory function
def get_deep_scraper(platform: str):
    """Get the appropriate deep scraper for a platform."""
    scrapers = {
        "reddit": DeepRedditScraper,
        "youtube": DeepYouTubeScraper,
        "twitter": BulkTwitterScraper
    }
    scraper_class = scrapers.get(platform)
    if scraper_class:
        return scraper_class()
    return None
