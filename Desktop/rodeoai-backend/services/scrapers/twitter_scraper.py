"""
Twitter/X Scraper
Scrapes public Twitter/X profiles and tweets using Playwright.
Note: Twitter heavily relies on JavaScript and has anti-bot measures.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..playwright_scraper import PlaywrightScraper
from ..base_scraper import ScrapedPost, ScrapedProfile


class TwitterScraper(PlaywrightScraper):
    """
    Twitter/X scraper using Playwright for JavaScript rendering.
    Handles Twitter's dynamic content loading.
    """

    BASE_URL = "https://twitter.com"
    X_URL = "https://x.com"

    def __init__(self, headless: bool = True):
        super().__init__(browser_type="chromium", headless=headless)
        self.platform = "twitter"

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a Twitter profile.

        Args:
            username: Twitter username (without @)

        Returns:
            ScrapedProfile object or None if profile not found
        """
        username = username.lstrip("@")
        url = f"{self.X_URL}/{username}"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # Wait for dynamic content

            # Check if profile exists
            if await page.query_selector('[data-testid="empty_state_header_text"]'):
                self.logger.warning(f"Profile not found: {username}")
                return None

            # Extract profile data
            profile_data = await page.evaluate("""
                () => {
                    const getName = () => {
                        const nameEl = document.querySelector('[data-testid="UserName"]');
                        if (nameEl) {
                            const spans = nameEl.querySelectorAll('span');
                            return spans[0]?.innerText || '';
                        }
                        return '';
                    };

                    const getBio = () => {
                        const bioEl = document.querySelector('[data-testid="UserDescription"]');
                        return bioEl?.innerText || '';
                    };

                    const getStats = () => {
                        const stats = {};
                        const links = document.querySelectorAll('a[href*="/following"], a[href*="/followers"], a[href*="/verified_followers"]');
                        links.forEach(link => {
                            const text = link.innerText;
                            const href = link.getAttribute('href');
                            if (href.includes('/following')) {
                                stats.following = text;
                            } else if (href.includes('/followers') && !href.includes('verified')) {
                                stats.followers = text;
                            }
                        });
                        return stats;
                    };

                    const getProfileImage = () => {
                        const img = document.querySelector('img[src*="profile_images"]');
                        return img?.src || '';
                    };

                    const getVerified = () => {
                        return !!document.querySelector('[data-testid="icon-verified"]');
                    };

                    const getWebsite = () => {
                        const linkEl = document.querySelector('[data-testid="UserUrl"]');
                        return linkEl?.innerText || '';
                    };

                    return {
                        displayName: getName(),
                        bio: getBio(),
                        stats: getStats(),
                        profileImage: getProfileImage(),
                        verified: getVerified(),
                        website: getWebsite()
                    };
                }
            """)

            return ScrapedProfile(
                platform="twitter",
                username=username,
                display_name=profile_data.get("displayName", ""),
                bio=profile_data.get("bio"),
                followers=self._parse_count(profile_data.get("stats", {}).get("followers")),
                following=self._parse_count(profile_data.get("stats", {}).get("following")),
                profile_image_url=profile_data.get("profileImage"),
                website=profile_data.get("website"),
                verified=profile_data.get("verified", False),
                url=url
            )

        except Exception as e:
            self.logger.error(f"Error scraping Twitter profile {username}: {e}")
            return None
        finally:
            await page.close()

    async def scrape_posts(self, username: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Scrape tweets from a user's timeline.

        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets to scrape

        Returns:
            List of ScrapedPost objects
        """
        username = username.lstrip("@")
        url = f"{self.X_URL}/{username}"

        page = await self._new_page()
        posts = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll to load more tweets
            scroll_attempts = min(limit // 5 + 1, 5)
            for _ in range(scroll_attempts):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)

            # Extract tweets
            tweets_data = await page.evaluate("""
                (limit) => {
                    const tweets = [];
                    const tweetElements = document.querySelectorAll('[data-testid="tweet"]');

                    for (let i = 0; i < Math.min(tweetElements.length, limit); i++) {
                        const tweet = tweetElements[i];

                        const getText = () => {
                            const textEl = tweet.querySelector('[data-testid="tweetText"]');
                            return textEl?.innerText || '';
                        };

                        const getTime = () => {
                            const timeEl = tweet.querySelector('time');
                            return timeEl?.getAttribute('datetime') || '';
                        };

                        const getStats = () => {
                            const stats = {};
                            const groups = tweet.querySelectorAll('[role="group"]');
                            if (groups.length > 0) {
                                const buttons = groups[0].querySelectorAll('[data-testid]');
                                buttons.forEach(btn => {
                                    const testId = btn.getAttribute('data-testid');
                                    const count = btn.querySelector('span')?.innerText || '0';
                                    if (testId.includes('reply')) stats.replies = count;
                                    if (testId.includes('retweet')) stats.retweets = count;
                                    if (testId.includes('like')) stats.likes = count;
                                });
                            }
                            return stats;
                        };

                        const getMedia = () => {
                            const media = [];
                            const images = tweet.querySelectorAll('img[src*="media"]');
                            images.forEach(img => media.push(img.src));
                            return media;
                        };

                        const getLink = () => {
                            const linkEl = tweet.querySelector('a[href*="/status/"]');
                            return linkEl?.href || '';
                        };

                        tweets.push({
                            text: getText(),
                            timestamp: getTime(),
                            stats: getStats(),
                            media: getMedia(),
                            link: getLink()
                        });
                    }

                    return tweets;
                }
            """, limit)

            for tweet_data in tweets_data:
                post_id = ""
                if tweet_data.get("link"):
                    match = re.search(r"/status/(\d+)", tweet_data["link"])
                    if match:
                        post_id = match.group(1)

                timestamp = None
                if tweet_data.get("timestamp"):
                    try:
                        timestamp = datetime.fromisoformat(tweet_data["timestamp"].replace("Z", "+00:00"))
                    except Exception:
                        pass

                posts.append(ScrapedPost(
                    platform="twitter",
                    post_id=post_id,
                    author=username,
                    author_handle=f"@{username}",
                    content=tweet_data.get("text", ""),
                    timestamp=timestamp,
                    likes=self._parse_count(tweet_data.get("stats", {}).get("likes")),
                    comments=self._parse_count(tweet_data.get("stats", {}).get("replies")),
                    shares=self._parse_count(tweet_data.get("stats", {}).get("retweets")),
                    media_urls=tweet_data.get("media", []),
                    url=tweet_data.get("link")
                ))

        except Exception as e:
            self.logger.error(f"Error scraping tweets from {username}: {e}")
        finally:
            await page.close()

        return posts[:limit]

    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Search for tweets by keyword or hashtag.

        Args:
            query: Search query (can include #hashtags)
            limit: Maximum number of results

        Returns:
            List of ScrapedPost objects
        """
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.X_URL}/search?q={encoded_query}&src=typed_query&f=live"

        page = await self._new_page()
        posts = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)

            # Scroll to load more results
            for _ in range(min(limit // 5 + 1, 3)):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1.5)

            # Extract search results (similar to timeline scraping)
            results = await page.evaluate("""
                (limit) => {
                    const tweets = [];
                    const tweetElements = document.querySelectorAll('[data-testid="tweet"]');

                    for (let i = 0; i < Math.min(tweetElements.length, limit); i++) {
                        const tweet = tweetElements[i];

                        const getAuthor = () => {
                            const userLink = tweet.querySelector('a[href^="/"][role="link"]');
                            if (userLink) {
                                const href = userLink.getAttribute('href');
                                return href?.replace('/', '') || '';
                            }
                            return '';
                        };

                        const getText = () => {
                            const textEl = tweet.querySelector('[data-testid="tweetText"]');
                            return textEl?.innerText || '';
                        };

                        const getTime = () => {
                            const timeEl = tweet.querySelector('time');
                            return timeEl?.getAttribute('datetime') || '';
                        };

                        const getLink = () => {
                            const linkEl = tweet.querySelector('a[href*="/status/"]');
                            return linkEl?.href || '';
                        };

                        tweets.push({
                            author: getAuthor(),
                            text: getText(),
                            timestamp: getTime(),
                            link: getLink()
                        });
                    }

                    return tweets;
                }
            """, limit)

            for result in results:
                post_id = ""
                if result.get("link"):
                    match = re.search(r"/status/(\d+)", result["link"])
                    if match:
                        post_id = match.group(1)

                posts.append(ScrapedPost(
                    platform="twitter",
                    post_id=post_id,
                    author=result.get("author", ""),
                    author_handle=f"@{result.get('author', '')}",
                    content=result.get("text", ""),
                    timestamp=None,
                    url=result.get("link")
                ))

        except Exception as e:
            self.logger.error(f"Error searching Twitter for '{query}': {e}")
        finally:
            await page.close()

        return posts[:limit]

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a specific tweet URL."""
        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            tweet_data = await page.evaluate("""
                () => {
                    const tweet = document.querySelector('[data-testid="tweet"]');
                    if (!tweet) return null;

                    return {
                        text: tweet.querySelector('[data-testid="tweetText"]')?.innerText || '',
                        author: document.querySelector('[data-testid="User-Name"]')?.innerText || '',
                        timestamp: tweet.querySelector('time')?.getAttribute('datetime') || '',
                        likes: tweet.querySelector('[data-testid="like"]')?.innerText || '0',
                        retweets: tweet.querySelector('[data-testid="retweet"]')?.innerText || '0',
                        replies: tweet.querySelector('[data-testid="reply"]')?.innerText || '0'
                    };
                }
            """)

            return {
                "url": url,
                "platform": "twitter",
                "data": tweet_data,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "url": url}
        finally:
            await page.close()
