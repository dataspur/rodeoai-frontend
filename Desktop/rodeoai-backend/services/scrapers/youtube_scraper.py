"""
YouTube Scraper
Scrapes YouTube channels, videos, and search results.
Uses public pages and meta tags for data extraction.
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..playwright_scraper import PlaywrightScraper
from ..base_scraper import ScrapedPost, ScrapedProfile


class YouTubeScraper(PlaywrightScraper):
    """
    YouTube scraper using Playwright for dynamic content.
    Extracts channel info, video details, and search results.
    """

    BASE_URL = "https://www.youtube.com"

    def __init__(self, headless: bool = True):
        super().__init__(browser_type="chromium", headless=headless)
        self.platform = "youtube"

    async def scrape_profile(self, channel_handle: str) -> Optional[ScrapedProfile]:
        """
        Scrape a YouTube channel profile.

        Args:
            channel_handle: Channel handle (@username) or channel ID

        Returns:
            ScrapedProfile object or None
        """
        # Handle different URL formats
        if channel_handle.startswith("@"):
            url = f"{self.BASE_URL}/{channel_handle}"
        elif channel_handle.startswith("UC"):
            url = f"{self.BASE_URL}/channel/{channel_handle}"
        else:
            url = f"{self.BASE_URL}/@{channel_handle}"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Extract channel data
            channel_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`) ||
                                   document.querySelector(`link[itemprop="${name}"]`);
                        return el?.content || el?.href || '';
                    };

                    // Try to get subscriber count from page
                    let subscribers = '';
                    const subElement = document.querySelector('#subscriber-count');
                    if (subElement) {
                        subscribers = subElement.innerText;
                    } else {
                        // Try meta description
                        const desc = getMeta('og:description') || getMeta('description');
                        const match = desc.match(/([\\d.]+[KMB]?)\\s*subscribers/i);
                        if (match) subscribers = match[1];
                    }

                    // Get channel name
                    const nameEl = document.querySelector('#channel-name, .ytd-channel-name');
                    const channelName = nameEl?.innerText || getMeta('og:title')?.replace(' - YouTube', '') || '';

                    // Get channel description
                    const descEl = document.querySelector('#description-container, [itemprop="description"]');
                    const description = descEl?.innerText || getMeta('og:description') || '';

                    // Get avatar
                    const avatarEl = document.querySelector('#avatar img, .yt-spec-avatar-shape img');
                    const avatar = avatarEl?.src || getMeta('og:image') || '';

                    // Check if verified
                    const verified = !!document.querySelector('[aria-label="Verified"], .badge-style-type-verified');

                    return {
                        name: channelName,
                        description: description,
                        avatar: avatar,
                        subscribers: subscribers,
                        verified: verified,
                        url: getMeta('og:url') || window.location.href
                    };
                }
            """)

            return ScrapedProfile(
                platform="youtube",
                username=channel_handle.lstrip("@"),
                display_name=channel_data.get("name", ""),
                bio=channel_data.get("description", "")[:500],
                followers=self._parse_count(channel_data.get("subscribers")),
                profile_image_url=channel_data.get("avatar"),
                verified=channel_data.get("verified", False),
                url=channel_data.get("url", url)
            )

        except Exception as e:
            self.logger.error(f"Error scraping YouTube channel {channel_handle}: {e}")
            return None
        finally:
            await page.close()

    async def scrape_video(self, video_id: str) -> Dict[str, Any]:
        """
        Scrape details from a YouTube video.

        Args:
            video_id: YouTube video ID (11 characters)

        Returns:
            Dictionary with video details
        """
        url = f"{self.BASE_URL}/watch?v={video_id}"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            video_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`) ||
                                   document.querySelector(`meta[itemprop="${name}"]`);
                        return el?.content || '';
                    };

                    // Get view count
                    let views = '';
                    const viewEl = document.querySelector('#info-strings yt-formatted-string, .view-count');
                    if (viewEl) {
                        views = viewEl.innerText;
                    }

                    // Get likes
                    let likes = '';
                    const likeButton = document.querySelector('[aria-label*="like this video"]');
                    if (likeButton) {
                        const likeText = likeButton.getAttribute('aria-label');
                        const match = likeText?.match(/([\\d,]+)/);
                        if (match) likes = match[1];
                    }

                    // Get channel info
                    const channelEl = document.querySelector('#channel-name a, ytd-channel-name a');
                    const channelName = channelEl?.innerText || '';
                    const channelUrl = channelEl?.href || '';

                    // Get publish date
                    const dateEl = document.querySelector('#info-strings yt-formatted-string:last-child');
                    let publishDate = dateEl?.innerText || '';

                    // Get description
                    const descEl = document.querySelector('#description-inline-expander, [itemprop="description"]');
                    const description = descEl?.innerText || getMeta('og:description') || '';

                    return {
                        title: getMeta('og:title') || getMeta('title') || document.title,
                        description: description,
                        thumbnail: getMeta('og:image'),
                        duration: getMeta('duration'),
                        views: views,
                        likes: likes,
                        channelName: channelName,
                        channelUrl: channelUrl,
                        publishDate: publishDate,
                        url: getMeta('og:url')
                    };
                }
            """)

            return {
                "platform": "youtube",
                "type": "video",
                "video_id": video_id,
                "title": video_data.get("title", ""),
                "description": video_data.get("description", "")[:2000],
                "thumbnail_url": video_data.get("thumbnail"),
                "duration": video_data.get("duration"),
                "views": self._parse_count(video_data.get("views", "").replace(" views", "")),
                "likes": self._parse_count(video_data.get("likes")),
                "channel_name": video_data.get("channelName"),
                "channel_url": video_data.get("channelUrl"),
                "publish_date": video_data.get("publishDate"),
                "url": url,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error scraping YouTube video {video_id}: {e}")
            return {"error": str(e), "url": url}
        finally:
            await page.close()

    async def scrape_posts(self, channel_handle: str, limit: int = 12) -> List[ScrapedPost]:
        """
        Scrape recent videos from a YouTube channel.

        Args:
            channel_handle: Channel handle or ID
            limit: Maximum videos to scrape

        Returns:
            List of ScrapedPost objects (representing videos)
        """
        # Handle different URL formats
        if channel_handle.startswith("@"):
            url = f"{self.BASE_URL}/{channel_handle}/videos"
        elif channel_handle.startswith("UC"):
            url = f"{self.BASE_URL}/channel/{channel_handle}/videos"
        else:
            url = f"{self.BASE_URL}/@{channel_handle}/videos"

        page = await self._new_page()
        posts = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll to load more videos
            for _ in range(min(limit // 12 + 1, 3)):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)

            # Extract video links and metadata
            videos_data = await page.evaluate("""
                (limit) => {
                    const videos = [];
                    const videoElements = document.querySelectorAll('ytd-rich-item-renderer, ytd-grid-video-renderer');

                    for (let i = 0; i < Math.min(videoElements.length, limit); i++) {
                        const el = videoElements[i];

                        const titleEl = el.querySelector('#video-title, #video-title-link');
                        const title = titleEl?.innerText || titleEl?.getAttribute('title') || '';
                        const href = titleEl?.href || '';

                        const thumbnailEl = el.querySelector('img');
                        const thumbnail = thumbnailEl?.src || '';

                        const metaEl = el.querySelector('#metadata-line');
                        const metaText = metaEl?.innerText || '';

                        // Parse views and time
                        const viewsMatch = metaText.match(/([\\d,.]+[KMB]?)\\s*views/i);
                        const timeMatch = metaText.match(/(\\d+\\s+\\w+\\s+ago|Streamed.*ago)/i);

                        videos.push({
                            title: title,
                            url: href,
                            thumbnail: thumbnail,
                            views: viewsMatch ? viewsMatch[1] : '',
                            publishedAgo: timeMatch ? timeMatch[1] : ''
                        });
                    }

                    return videos;
                }
            """, limit)

            for video_data in videos_data:
                # Extract video ID from URL
                video_id = ""
                url_match = re.search(r"[?&]v=([^&]+)", video_data.get("url", ""))
                if url_match:
                    video_id = url_match.group(1)

                posts.append(ScrapedPost(
                    platform="youtube",
                    post_id=video_id,
                    author=channel_handle.lstrip("@"),
                    author_handle=channel_handle if channel_handle.startswith("@") else f"@{channel_handle}",
                    content=video_data.get("title", ""),
                    timestamp=None,  # Would need to parse "X days ago"
                    likes=self._parse_count(video_data.get("views")),  # Using views as likes for now
                    media_urls=[video_data.get("thumbnail")] if video_data.get("thumbnail") else [],
                    url=video_data.get("url"),
                    raw_data={"published_ago": video_data.get("publishedAgo")}
                ))

        except Exception as e:
            self.logger.error(f"Error scraping YouTube channel videos {channel_handle}: {e}")
        finally:
            await page.close()

        return posts[:limit]

    async def search_posts(self, query: str, limit: int = 20) -> List[ScrapedPost]:
        """
        Search YouTube for videos.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of ScrapedPost objects
        """
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        url = f"{self.BASE_URL}/results?search_query={encoded_query}"

        page = await self._new_page()
        posts = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll for more results
            for _ in range(min(limit // 20 + 1, 3)):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)

            # Extract search results
            results_data = await page.evaluate("""
                (limit) => {
                    const results = [];
                    const videoElements = document.querySelectorAll('ytd-video-renderer');

                    for (let i = 0; i < Math.min(videoElements.length, limit); i++) {
                        const el = videoElements[i];

                        const titleEl = el.querySelector('#video-title');
                        const title = titleEl?.innerText || titleEl?.getAttribute('title') || '';
                        const href = titleEl?.href || '';

                        const channelEl = el.querySelector('.ytd-channel-name a');
                        const channelName = channelEl?.innerText || '';
                        const channelUrl = channelEl?.href || '';

                        const thumbnailEl = el.querySelector('img');
                        const thumbnail = thumbnailEl?.src || '';

                        const metaEl = el.querySelector('#metadata-line');
                        const metaText = metaEl?.innerText || '';

                        const viewsMatch = metaText.match(/([\\d,.]+[KMB]?)\\s*views/i);

                        results.push({
                            title: title,
                            url: href,
                            thumbnail: thumbnail,
                            channelName: channelName,
                            channelUrl: channelUrl,
                            views: viewsMatch ? viewsMatch[1] : ''
                        });
                    }

                    return results;
                }
            """, limit)

            for result in results_data:
                video_id = ""
                url_match = re.search(r"[?&]v=([^&]+)", result.get("url", ""))
                if url_match:
                    video_id = url_match.group(1)

                posts.append(ScrapedPost(
                    platform="youtube",
                    post_id=video_id,
                    author=result.get("channelName", ""),
                    author_handle=None,
                    content=result.get("title", ""),
                    timestamp=None,
                    likes=self._parse_count(result.get("views")),
                    media_urls=[result.get("thumbnail")] if result.get("thumbnail") else [],
                    url=result.get("url"),
                    raw_data={"channel_url": result.get("channelUrl")}
                ))

        except Exception as e:
            self.logger.error(f"Error searching YouTube for '{query}': {e}")
        finally:
            await page.close()

        return posts[:limit]

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape any YouTube URL."""
        # Video URL
        video_match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
        if video_match:
            return await self.scrape_video(video_match.group(1))

        # Channel URL
        channel_match = re.search(r"(?:/@|/channel/|/c/)([^/\?]+)", url)
        if channel_match:
            handle = channel_match.group(1)
            if "/channel/" in url:
                profile = await self.scrape_profile(handle)
            else:
                profile = await self.scrape_profile(f"@{handle}")
            return profile.to_dict() if profile else {"error": "Failed to scrape channel", "url": url}

        return {"error": "Unsupported YouTube URL type", "url": url}
