"""
LinkedIn Scraper
Scrapes public LinkedIn profiles and company pages.
Note: LinkedIn has strict scraping policies and rate limiting.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..playwright_scraper import PlaywrightScraper
from ..base_scraper import ScrapedPost, ScrapedProfile


class LinkedInScraper(PlaywrightScraper):
    """
    LinkedIn scraper for public profiles and company pages.
    Note: Most LinkedIn content requires authentication.
    """

    BASE_URL = "https://www.linkedin.com"

    def __init__(self, headless: bool = True):
        super().__init__(browser_type="chromium", headless=headless)
        self.platform = "linkedin"

    async def scrape_profile(self, username: str) -> Optional[ScrapedProfile]:
        """
        Scrape a public LinkedIn profile.

        Args:
            username: LinkedIn profile URL slug (e.g., 'john-doe-123456')

        Returns:
            ScrapedProfile object or None
        """
        url = f"{self.BASE_URL}/in/{username}/"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Check for auth wall
            if await page.query_selector('[data-test-id="join-form"]'):
                self.logger.warning("LinkedIn auth wall encountered")
                # Try to get limited public data
                return await self._scrape_public_profile(page, url, username)

            # Extract profile data from meta tags (works without login)
            profile_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`);
                        return el?.content || '';
                    };

                    return {
                        title: getMeta('og:title'),
                        description: getMeta('og:description'),
                        image: getMeta('og:image'),
                        url: getMeta('og:url'),
                        type: getMeta('og:type')
                    };
                }
            """)

            # Parse name and headline from title
            title = profile_data.get("title", "")
            name_parts = title.split(" - LinkedIn") if " - LinkedIn" in title else [title]
            name_headline = name_parts[0].split(" | ") if name_parts else ["", ""]

            display_name = name_headline[0].strip() if name_headline else ""
            headline = name_headline[1].strip() if len(name_headline) > 1 else ""

            return ScrapedProfile(
                platform="linkedin",
                username=username,
                display_name=display_name,
                bio=headline or profile_data.get("description"),
                profile_image_url=profile_data.get("image"),
                url=url
            )

        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn profile {username}: {e}")
            return None
        finally:
            await page.close()

    async def _scrape_public_profile(self, page, url: str, username: str) -> Optional[ScrapedProfile]:
        """Extract what's available from public view."""
        try:
            profile_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`);
                        return el?.content || '';
                    };

                    // Try to get public profile card info
                    const nameEl = document.querySelector('.top-card-layout__title');
                    const headlineEl = document.querySelector('.top-card-layout__headline');
                    const locationEl = document.querySelector('.top-card-layout__first-subline');
                    const imageEl = document.querySelector('.top-card-layout__entity-image');

                    return {
                        name: nameEl?.innerText || getMeta('og:title')?.split(' - ')[0] || '',
                        headline: headlineEl?.innerText || '',
                        location: locationEl?.innerText || '',
                        image: imageEl?.src || getMeta('og:image'),
                        description: getMeta('og:description')
                    };
                }
            """)

            return ScrapedProfile(
                platform="linkedin",
                username=username,
                display_name=profile_data.get("name", ""),
                bio=profile_data.get("headline") or profile_data.get("description"),
                profile_image_url=profile_data.get("image"),
                website=profile_data.get("location"),  # Using website field for location
                url=url
            )
        except Exception as e:
            self.logger.error(f"Error scraping public profile: {e}")
            return None

    async def scrape_company(self, company_slug: str) -> Dict[str, Any]:
        """
        Scrape a LinkedIn company page.

        Args:
            company_slug: Company page URL slug

        Returns:
            Dictionary with company data
        """
        url = f"{self.BASE_URL}/company/{company_slug}/"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            company_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`);
                        return el?.content || '';
                    };

                    // Try to get company info
                    const nameEl = document.querySelector('.top-card-layout__title, .org-top-card-summary__title');
                    const descEl = document.querySelector('.top-card-layout__second-subline, .org-top-card-summary__tagline');
                    const followersEl = document.querySelector('.top-card-layout__first-subline');

                    // Parse followers count
                    let followers = '';
                    const followersText = followersEl?.innerText || '';
                    const followersMatch = followersText.match(/([\\d,]+)\\s*followers/i);
                    if (followersMatch) followers = followersMatch[1];

                    return {
                        name: nameEl?.innerText || getMeta('og:title')?.replace(' | LinkedIn', '') || '',
                        description: descEl?.innerText || getMeta('og:description') || '',
                        image: getMeta('og:image'),
                        followers: followers,
                        url: getMeta('og:url')
                    };
                }
            """)

            return {
                "platform": "linkedin",
                "type": "company",
                "name": company_data.get("name", ""),
                "description": company_data.get("description", ""),
                "logo_url": company_data.get("image"),
                "followers": self._parse_count(company_data.get("followers")),
                "url": url,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn company {company_slug}: {e}")
            return {"error": str(e), "url": url}
        finally:
            await page.close()

    async def scrape_posts(self, username: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Scrape posts from a LinkedIn profile.
        Note: LinkedIn requires login for most post content.
        """
        self.logger.warning("LinkedIn post scraping requires authentication")
        return []

    async def search_posts(self, query: str, limit: int = 10) -> List[ScrapedPost]:
        """
        Search LinkedIn posts.
        Note: LinkedIn search requires authentication.
        """
        self.logger.warning("LinkedIn search requires authentication")
        return []

    async def scrape_job_posting(self, job_id: str) -> Dict[str, Any]:
        """
        Scrape a public LinkedIn job posting.

        Args:
            job_id: LinkedIn job ID

        Returns:
            Dictionary with job details
        """
        url = f"{self.BASE_URL}/jobs/view/{job_id}/"

        page = await self._new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            job_data = await page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const el = document.querySelector(`meta[property="${name}"]`) ||
                                   document.querySelector(`meta[name="${name}"]`);
                        return el?.content || '';
                    };

                    // Try to get job info
                    const titleEl = document.querySelector('.top-card-layout__title, .topcard__title');
                    const companyEl = document.querySelector('.topcard__org-name-link, .top-card-layout__second-subline a');
                    const locationEl = document.querySelector('.topcard__flavor--bullet, .top-card-layout__second-subline');
                    const descEl = document.querySelector('.description__text, .show-more-less-html__markup');

                    return {
                        title: titleEl?.innerText || getMeta('og:title')?.split(' | ')[0] || '',
                        company: companyEl?.innerText || '',
                        location: locationEl?.innerText || '',
                        description: descEl?.innerText || getMeta('og:description') || '',
                        image: getMeta('og:image')
                    };
                }
            """)

            return {
                "platform": "linkedin",
                "type": "job",
                "job_id": job_id,
                "title": job_data.get("title", ""),
                "company": job_data.get("company", ""),
                "location": job_data.get("location", ""),
                "description": job_data.get("description", "")[:5000],
                "url": url,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn job {job_id}: {e}")
            return {"error": str(e), "url": url}
        finally:
            await page.close()

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape any LinkedIn URL."""
        if "/in/" in url:
            # Profile URL
            username = url.split("/in/")[1].rstrip("/").split("/")[0]
            profile = await self.scrape_profile(username)
            return profile.to_dict() if profile else {"error": "Failed to scrape profile", "url": url}
        elif "/company/" in url:
            # Company URL
            company_slug = url.split("/company/")[1].rstrip("/").split("/")[0]
            return await self.scrape_company(company_slug)
        elif "/jobs/view/" in url:
            # Job URL
            job_id = url.split("/jobs/view/")[1].rstrip("/").split("/")[0]
            return await self.scrape_job_posting(job_id)
        else:
            return {"error": "Unsupported LinkedIn URL type", "url": url}
