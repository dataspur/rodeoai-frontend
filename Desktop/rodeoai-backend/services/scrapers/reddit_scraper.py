"""
Reddit Scraper
Scrapes Reddit profiles, subreddits, and posts.
Reddit has a relatively accessible public API and structure.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..beautifulsoup_scraper import BeautifulSoupScraper
from ..base_scraper import ScrapedPost, ScrapedProfile


class RedditScraper(BeautifulSoupScraper):
    """
    Reddit scraper using BeautifulSoup for the old Reddit interface
    and JSON endpoints which are more reliable.
    """

    BASE_URL = "https://old.reddit.com"
    JSON_URL = "https://www.reddit.com"

    def __init__(self):
        super().__init__()
        self.platform = "reddit"
        # Update headers for Reddit
        self.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; RodeoAI/1.0; +https://rodeoai.com)"
        })

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a Reddit user profile.

        Args:
            username: Reddit username (without u/)

        Returns:
            ScrapedProfile object or None
        """
        username = username.lstrip("u/").lstrip("/")

        # Try JSON endpoint first
        json_url = f"{self.JSON_URL}/user/{username}/about.json"

        try:
            session = await self._get_session()
            async with session.get(json_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    user_data = data.get("data", {})

                    return ScrapedProfile(
                        platform="reddit",
                        username=username,
                        display_name=user_data.get("subreddit", {}).get("title", username),
                        bio=user_data.get("subreddit", {}).get("public_description", ""),
                        followers=user_data.get("subreddit", {}).get("subscribers", 0),
                        post_count=user_data.get("total_karma", 0),  # Using karma as post count
                        profile_image_url=user_data.get("icon_img", "").split("?")[0],
                        verified=user_data.get("verified", False),
                        url=f"https://reddit.com/user/{username}"
                    )
        except Exception as e:
            self.logger.error(f"Error fetching Reddit user JSON: {e}")

        return None

    async def scrape_posts(self, username: str, limit: int = 25) -> List[ScrapedPost]:
        """
        Scrape posts from a Reddit user.

        Args:
            username: Reddit username
            limit: Maximum posts to fetch (max 100)

        Returns:
            List of ScrapedPost objects
        """
        username = username.lstrip("u/").lstrip("/")
        json_url = f"{self.JSON_URL}/user/{username}/submitted.json?limit={min(limit, 100)}"

        posts = []

        try:
            session = await self._get_session()
            async with session.get(json_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    children = data.get("data", {}).get("children", [])

                    for child in children[:limit]:
                        post_data = child.get("data", {})

                        timestamp = None
                        if post_data.get("created_utc"):
                            timestamp = datetime.utcfromtimestamp(post_data["created_utc"])

                        # Get media URLs
                        media_urls = []
                        if post_data.get("url") and any(
                            ext in post_data["url"] for ext in [".jpg", ".png", ".gif", ".jpeg"]
                        ):
                            media_urls.append(post_data["url"])
                        elif post_data.get("thumbnail") and post_data["thumbnail"].startswith("http"):
                            media_urls.append(post_data["thumbnail"])

                        posts.append(ScrapedPost(
                            platform="reddit",
                            post_id=post_data.get("id", ""),
                            author=username,
                            author_handle=f"u/{username}",
                            content=f"{post_data.get('title', '')}\n\n{post_data.get('selftext', '')}".strip(),
                            timestamp=timestamp,
                            likes=post_data.get("ups", 0),
                            comments=post_data.get("num_comments", 0),
                            media_urls=media_urls,
                            url=f"https://reddit.com{post_data.get('permalink', '')}"
                        ))

        except Exception as e:
            self.logger.error(f"Error fetching Reddit user posts: {e}")

        return posts

    async def scrape_subreddit(self, subreddit: str, sort: str = "hot", limit: int = 25) -> List[ScrapedPost]:
        """
        Scrape posts from a subreddit.

        Args:
            subreddit: Subreddit name (without r/)
            sort: Sort method (hot, new, top, rising)
            limit: Maximum posts to fetch

        Returns:
            List of ScrapedPost objects
        """
        subreddit = subreddit.lstrip("r/").lstrip("/")
        json_url = f"{self.JSON_URL}/r/{subreddit}/{sort}.json?limit={min(limit, 100)}"

        posts = []

        try:
            session = await self._get_session()
            async with session.get(json_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    children = data.get("data", {}).get("children", [])

                    for child in children[:limit]:
                        post_data = child.get("data", {})

                        timestamp = None
                        if post_data.get("created_utc"):
                            timestamp = datetime.utcfromtimestamp(post_data["created_utc"])

                        media_urls = []
                        if post_data.get("url") and any(
                            ext in post_data["url"].lower() for ext in [".jpg", ".png", ".gif", ".jpeg", ".webp"]
                        ):
                            media_urls.append(post_data["url"])

                        posts.append(ScrapedPost(
                            platform="reddit",
                            post_id=post_data.get("id", ""),
                            author=post_data.get("author", "[deleted]"),
                            author_handle=f"u/{post_data.get('author', '[deleted]')}",
                            content=f"{post_data.get('title', '')}\n\n{post_data.get('selftext', '')}".strip(),
                            timestamp=timestamp,
                            likes=post_data.get("ups", 0),
                            comments=post_data.get("num_comments", 0),
                            media_urls=media_urls,
                            url=f"https://reddit.com{post_data.get('permalink', '')}",
                            raw_data={"subreddit": subreddit, "flair": post_data.get("link_flair_text")}
                        ))

        except Exception as e:
            self.logger.error(f"Error fetching subreddit posts: {e}")

        return posts

    async def scrape_subreddit_info(self, subreddit: str) -> Dict[str, Any]:
        """
        Get information about a subreddit.

        Args:
            subreddit: Subreddit name

        Returns:
            Dictionary with subreddit info
        """
        subreddit = subreddit.lstrip("r/").lstrip("/")
        json_url = f"{self.JSON_URL}/r/{subreddit}/about.json"

        try:
            session = await self._get_session()
            async with session.get(json_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    sub_data = data.get("data", {})

                    return {
                        "platform": "reddit",
                        "type": "subreddit",
                        "name": sub_data.get("display_name", subreddit),
                        "title": sub_data.get("title", ""),
                        "description": sub_data.get("public_description", ""),
                        "subscribers": sub_data.get("subscribers", 0),
                        "active_users": sub_data.get("accounts_active", 0),
                        "created_utc": sub_data.get("created_utc"),
                        "nsfw": sub_data.get("over18", False),
                        "icon_url": sub_data.get("icon_img", "").split("?")[0],
                        "banner_url": sub_data.get("banner_img", "").split("?")[0],
                        "url": f"https://reddit.com/r/{subreddit}",
                        "scraped_at": datetime.utcnow().isoformat()
                    }

        except Exception as e:
            self.logger.error(f"Error fetching subreddit info: {e}")

        return {"error": "Failed to fetch subreddit", "subreddit": subreddit}

    async def search_posts(self, query: str, limit: int = 25, subreddit: str = None) -> List[ScrapedPost]:
        """
        Search Reddit posts.

        Args:
            query: Search query
            limit: Maximum results
            subreddit: Optional subreddit to search within

        Returns:
            List of ScrapedPost objects
        """
        import urllib.parse
        encoded_query = urllib.parse.quote(query)

        if subreddit:
            json_url = f"{self.JSON_URL}/r/{subreddit}/search.json?q={encoded_query}&restrict_sr=1&limit={min(limit, 100)}"
        else:
            json_url = f"{self.JSON_URL}/search.json?q={encoded_query}&limit={min(limit, 100)}"

        posts = []

        try:
            session = await self._get_session()
            async with session.get(json_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    children = data.get("data", {}).get("children", [])

                    for child in children[:limit]:
                        post_data = child.get("data", {})

                        timestamp = None
                        if post_data.get("created_utc"):
                            timestamp = datetime.utcfromtimestamp(post_data["created_utc"])

                        posts.append(ScrapedPost(
                            platform="reddit",
                            post_id=post_data.get("id", ""),
                            author=post_data.get("author", "[deleted]"),
                            author_handle=f"u/{post_data.get('author', '[deleted]')}",
                            content=f"{post_data.get('title', '')}\n\n{post_data.get('selftext', '')}".strip(),
                            timestamp=timestamp,
                            likes=post_data.get("ups", 0),
                            comments=post_data.get("num_comments", 0),
                            url=f"https://reddit.com{post_data.get('permalink', '')}",
                            raw_data={"subreddit": post_data.get("subreddit")}
                        ))

        except Exception as e:
            self.logger.error(f"Error searching Reddit: {e}")

        return posts

    async def scrape_post_comments(self, post_url: str, limit: int = 50) -> Dict[str, Any]:
        """
        Scrape comments from a Reddit post.

        Args:
            post_url: URL to the Reddit post
            limit: Maximum comments to fetch

        Returns:
            Dictionary with post and comments data
        """
        # Convert to JSON URL
        if not post_url.endswith(".json"):
            post_url = post_url.rstrip("/") + ".json"

        try:
            session = await self._get_session()
            async with session.get(post_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()

                    # First item is the post, second is comments
                    post_data = data[0]["data"]["children"][0]["data"] if data else {}
                    comments_data = data[1]["data"]["children"] if len(data) > 1 else []

                    comments = []
                    for comment in comments_data[:limit]:
                        if comment.get("kind") != "t1":
                            continue
                        c_data = comment.get("data", {})
                        comments.append({
                            "id": c_data.get("id"),
                            "author": c_data.get("author"),
                            "body": c_data.get("body", ""),
                            "score": c_data.get("score", 0),
                            "created_utc": c_data.get("created_utc")
                        })

                    return {
                        "platform": "reddit",
                        "post": {
                            "id": post_data.get("id"),
                            "title": post_data.get("title"),
                            "author": post_data.get("author"),
                            "content": post_data.get("selftext"),
                            "score": post_data.get("score"),
                            "num_comments": post_data.get("num_comments")
                        },
                        "comments": comments,
                        "scraped_at": datetime.utcnow().isoformat()
                    }

        except Exception as e:
            self.logger.error(f"Error fetching Reddit comments: {e}")

        return {"error": "Failed to fetch comments", "url": post_url}

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape any Reddit URL."""
        if "/user/" in url or "/u/" in url:
            # User profile
            match = re.search(r"/(?:user|u)/([^/]+)", url)
            if match:
                username = match.group(1)
                profile = await self.scrape_profile(username)
                return profile.to_dict() if profile else {"error": "Failed to scrape profile", "url": url}

        elif "/r/" in url:
            # Subreddit or post
            if "/comments/" in url:
                # It's a post
                return await self.scrape_post_comments(url)
            else:
                # It's a subreddit
                match = re.search(r"/r/([^/]+)", url)
                if match:
                    return await self.scrape_subreddit_info(match.group(1))

        return {"error": "Unsupported Reddit URL type", "url": url}
