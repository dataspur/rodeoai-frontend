"""
Instagram Scraper
Scrapes public Instagram profiles and posts using Playwright.
Note: Instagram requires login for most content; this handles public profiles.
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..playwright_scraper import PlaywrightScraper
from ..base_scraper import ScrapedPost, ScrapedProfile


class InstagramScraper(PlaywrightScraper):
    """
    Instagram scraper using Playwright.
    Handles public Instagram profiles and posts.
    """

    BASE_URL = "https://www.instagram.com"

    def __init__(self, headless: bool = True):
        super().__init__(browser_type="chromium", headless=headless)
        self.platform = "instagram"

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a public Instagram profile.

        Args:
            username: Instagram username (without @)

        Returns:
            ScrapedProfile object or None if profile not found/private
        """
        username = username.lstrip("@")
        url = f"{self.BASE_URL}/{username}/"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Check for login wall or 404
            page_content = await page.content()
            if "Page Not Found" in page_content or "Sorry, this page" in page_content:
                self.logger.warning(f"Profile not found: {username}")
                return None

            # Try to extract from JSON-LD or meta tags
            profile_data = await page.evaluate("""
                () => {
                    // Try to get from meta tags
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`);
                        return el?.content || '';
                    };

                    // Parse description for stats
                    const description = getMeta('og:description') || getMeta('description');

                    // Try to extract follower/following counts from description
                    // Format: "123 Followers, 45 Following, 67 Posts - description"
                    const statsMatch = description.match(/([\\d,.]+[KMB]?)\\s*Followers/i);
                    const followingMatch = description.match(/([\\d,.]+[KMB]?)\\s*Following/i);
                    const postsMatch = description.match(/([\\d,.]+[KMB]?)\\s*Posts/i);

                    return {
                        displayName: getMeta('og:title')?.replace(' | Instagram', '').replace(' (@' + location.pathname.replace(/\\//g, '') + ')', '') || '',
                        description: description,
                        image: getMeta('og:image'),
                        followers: statsMatch ? statsMatch[1] : '',
                        following: followingMatch ? followingMatch[1] : '',
                        posts: postsMatch ? postsMatch[1] : '',
                        url: getMeta('og:url')
                    };
                }
            """)

            # Try to get more data from page structure
            additional_data = await page.evaluate("""
                () => {
                    const data = {};

                    // Try to find bio section
                    const bioSection = document.querySelector('section main header section');
                    if (bioSection) {
                        // Find stats list
                        const statsList = bioSection.querySelectorAll('ul li');
                        statsList.forEach(li => {
                            const text = li.innerText;
                            if (text.includes('posts')) data.posts = text.replace(/[^\\d]/g, '');
                            if (text.includes('followers')) data.followers = text.replace(/[^\\d]/g, '');
                            if (text.includes('following')) data.following = text.replace(/[^\\d]/g, '');
                        });

                        // Find bio text
                        const bioDiv = bioSection.querySelector('div > span');
                        if (bioDiv) data.bio = bioDiv.innerText;
                    }

                    // Check for verified badge
                    data.verified = !!document.querySelector('[aria-label="Verified"]');

                    return data;
                }
            """)

            # Merge data
            followers = additional_data.get("followers") or profile_data.get("followers", "")
            following = additional_data.get("following") or profile_data.get("following", "")
            posts = additional_data.get("posts") or profile_data.get("posts", "")

            return ScrapedProfile(
                platform="instagram",
                username=username,
                display_name=profile_data.get("displayName", username),
                bio=additional_data.get("bio") or self._extract_bio_from_description(profile_data.get("description", "")),
                followers=self._parse_count(followers),
                following=self._parse_count(following),
                post_count=self._parse_count(posts),
                profile_image_url=profile_data.get("image"),
                verified=additional_data.get("verified", False),
                url=url
            )

        except Exception as e:
            self.logger.error(f"Error scraping Instagram profile {username}: {e}")
            return None
        finally:
            await page.close()

    def _extract_bio_from_description(self, description: str) -> Optional[str]:
        """Extract bio from og:description."""
        if not description:
            return None
        # Remove stats portion
        parts = description.split(" - ", 1)
        if len(parts) > 1:
            return parts[1].strip()
        return None

    async def scrape_posts(self, username: str, limit: int = 12) -> List[ScrapedPost]:
        """
        Scrape posts from a public Instagram profile.

        Args:
            username: Instagram username
            limit: Maximum number of posts (multiples of 12 work best)

        Returns:
            List of ScrapedPost objects
        """
        username = username.lstrip("@")
        url = f"{self.BASE_URL}/{username}/"

        page = await self._new_page()
        posts = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll to load more posts
            scroll_count = min(limit // 12 + 1, 5)
            for _ in range(scroll_count):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1.5)

            # Extract post links and thumbnails
            posts_data = await page.evaluate("""
                (limit) => {
                    const posts = [];
                    const postLinks = document.querySelectorAll('a[href*="/p/"]');

                    const seen = new Set();
                    for (const link of postLinks) {
                        const href = link.getAttribute('href');
                        if (seen.has(href)) continue;
                        seen.add(href);

                        const img = link.querySelector('img');
                        posts.push({
                            url: 'https://www.instagram.com' + href,
                            shortcode: href.split('/p/')[1]?.replace('/', '') || '',
                            thumbnail: img?.src || ''
                        });

                        if (posts.length >= limit) break;
                    }

                    return posts;
                }
            """, limit)

            for post_data in posts_data:
                posts.append(ScrapedPost(
                    platform="instagram",
                    post_id=post_data.get("shortcode", ""),
                    author=username,
                    author_handle=f"@{username}",
                    content="",  # Would need to visit individual post for caption
                    timestamp=None,
                    media_urls=[post_data.get("thumbnail")] if post_data.get("thumbnail") else [],
                    url=post_data.get("url")
                ))

        except Exception as e:
            self.logger.error(f"Error scraping Instagram posts from {username}: {e}")
        finally:
            await page.close()

        return posts[:limit]

    async def scrape_post_details(self, post_url: str) -> Optional[ScrapedPost]:
        """
        Scrape details from a specific Instagram post.

        Args:
            post_url: Full URL to the Instagram post

        Returns:
            ScrapedPost object with full details
        """
        page = await self._new_page()

        try:
            await page.goto(post_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            post_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`);
                        return el?.content || '';
                    };

                    // Try to get caption from article
                    let caption = '';
                    const article = document.querySelector('article');
                    if (article) {
                        const captionSpan = article.querySelector('h1')?.parentElement?.querySelector('span');
                        if (captionSpan) caption = captionSpan.innerText;
                    }

                    // Get likes count
                    let likes = '';
                    const likesSection = document.querySelector('section');
                    if (likesSection) {
                        const likesText = likesSection.innerText;
                        const likesMatch = likesText.match(/([\\d,]+)\\s*likes?/i);
                        if (likesMatch) likes = likesMatch[1];
                    }

                    // Get timestamp
                    const timeEl = document.querySelector('time');
                    const timestamp = timeEl?.getAttribute('datetime') || '';

                    return {
                        title: getMeta('og:title'),
                        description: getMeta('og:description'),
                        image: getMeta('og:image'),
                        caption: caption || getMeta('og:description')?.split('"')[1] || '',
                        likes: likes,
                        timestamp: timestamp,
                        type: getMeta('og:type')
                    };
                }
            """)

            # Extract shortcode from URL
            shortcode_match = re.search(r"/p/([^/]+)", post_url)
            shortcode = shortcode_match.group(1) if shortcode_match else ""

            # Extract username from title
            author = ""
            title = post_data.get("title", "")
            if " on Instagram:" in title:
                author = title.split(" on Instagram:")[0].strip()

            return ScrapedPost(
                platform="instagram",
                post_id=shortcode,
                author=author,
                author_handle=f"@{author}" if author else None,
                content=post_data.get("caption", ""),
                timestamp=datetime.fromisoformat(post_data["timestamp"].replace("Z", "+00:00")) if post_data.get("timestamp") else None,
                likes=self._parse_count(post_data.get("likes")),
                media_urls=[post_data.get("image")] if post_data.get("image") else [],
                url=post_url
            )

        except Exception as e:
            self.logger.error(f"Error scraping Instagram post {post_url}: {e}")
            return None
        finally:
            await page.close()

    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Search Instagram posts by hashtag.

        Args:
            query: Hashtag to search (with or without #)
            limit: Maximum number of results

        Returns:
            List of ScrapedPost objects
        """
        # Clean up hashtag
        hashtag = query.lstrip("#").strip()
        url = f"{self.BASE_URL}/explore/tags/{hashtag}/"

        page = await self._new_page()
        posts = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll to load posts
            for _ in range(min(limit // 12 + 1, 3)):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1.5)

            # Extract posts
            posts_data = await page.evaluate("""
                (limit) => {
                    const posts = [];
                    const postLinks = document.querySelectorAll('a[href*="/p/"]');

                    const seen = new Set();
                    for (const link of postLinks) {
                        const href = link.getAttribute('href');
                        if (seen.has(href)) continue;
                        seen.add(href);

                        const img = link.querySelector('img');
                        posts.push({
                            url: 'https://www.instagram.com' + href,
                            shortcode: href.split('/p/')[1]?.replace('/', '') || '',
                            thumbnail: img?.src || ''
                        });

                        if (posts.length >= limit) break;
                    }

                    return posts;
                }
            """, limit)

            for post_data in posts_data:
                posts.append(ScrapedPost(
                    platform="instagram",
                    post_id=post_data.get("shortcode", ""),
                    author="",  # Unknown from hashtag search
                    author_handle=None,
                    content=f"#{hashtag}",
                    timestamp=None,
                    media_urls=[post_data.get("thumbnail")] if post_data.get("thumbnail") else [],
                    url=post_data.get("url")
                ))

        except Exception as e:
            self.logger.error(f"Error searching Instagram for #{hashtag}: {e}")
        finally:
            await page.close()

        return posts[:limit]

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape any Instagram URL."""
        if "/p/" in url:
            post = await self.scrape_post_details(url)
            return post.to_dict() if post else {"error": "Failed to scrape post", "url": url}
        elif url.rstrip("/").count("/") == 3:  # Profile URL
            username = url.rstrip("/").split("/")[-1]
            profile = await self.scrape_profile(username)
            return profile.to_dict() if profile else {"error": "Failed to scrape profile", "url": url}
        else:
            return {"error": "Unsupported Instagram URL type", "url": url}
