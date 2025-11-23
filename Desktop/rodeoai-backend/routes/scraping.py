"""
Social Media Scraping API Routes
Endpoints for scraping social media platforms.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio

# Import scrapers
from services.beautifulsoup_scraper import BeautifulSoupScraper
from services.selenium_scraper import SeleniumScraper
from services.playwright_scraper import PlaywrightScraper
from services.scrapers import (
    TwitterScraper,
    InstagramScraper,
    LinkedInScraper,
    RedditScraper,
    YouTubeScraper
)

router = APIRouter(prefix="/api/scrape", tags=["scraping"])


# --- Request Models ---

class Platform(str, Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    YOUTUBE = "youtube"


class ScraperEngine(str, Enum):
    BEAUTIFULSOUP = "beautifulsoup"
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"


class ProfileRequest(BaseModel):
    platform: Platform
    username: str = Field(..., description="Username/handle to scrape")


class PostsRequest(BaseModel):
    platform: Platform
    username: str = Field(..., description="Username/handle to scrape posts from")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum posts to retrieve")


class SearchRequest(BaseModel):
    platform: Platform
    query: str = Field(..., description="Search query or hashtag")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")


class UrlScrapeRequest(BaseModel):
    url: str = Field(..., description="URL to scrape")
    engine: ScraperEngine = Field(default=ScraperEngine.PLAYWRIGHT, description="Scraping engine to use")
    wait_selector: Optional[str] = Field(default=None, description="CSS selector to wait for (Playwright only)")


class ArticleScrapeRequest(BaseModel):
    url: str = Field(..., description="Article URL to scrape")


class SubredditRequest(BaseModel):
    subreddit: str = Field(..., description="Subreddit name (without r/)")
    sort: str = Field(default="hot", description="Sort method: hot, new, top, rising")
    limit: int = Field(default=25, ge=1, le=100)


class YouTubeVideoRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")


# --- Helper Functions ---

def get_platform_scraper(platform: Platform):
    """Get the appropriate scraper for a platform."""
    scrapers = {
        Platform.TWITTER: TwitterScraper,
        Platform.INSTAGRAM: InstagramScraper,
        Platform.LINKEDIN: LinkedInScraper,
        Platform.REDDIT: RedditScraper,
        Platform.YOUTUBE: YouTubeScraper,
    }
    return scrapers.get(platform)()


def get_engine_scraper(engine: ScraperEngine):
    """Get scraper by engine type."""
    engines = {
        ScraperEngine.BEAUTIFULSOUP: BeautifulSoupScraper,
        ScraperEngine.SELENIUM: SeleniumScraper,
        ScraperEngine.PLAYWRIGHT: PlaywrightScraper,
    }
    return engines.get(engine)()


# --- Profile Endpoints ---

@router.post("/profile", summary="Scrape a social media profile")
async def scrape_profile(request: ProfileRequest) -> Dict[str, Any]:
    """
    Scrape a user profile from a social media platform.

    Supported platforms:
    - **twitter**: Twitter/X profiles
    - **instagram**: Instagram profiles (public only)
    - **linkedin**: LinkedIn profiles (limited without auth)
    - **reddit**: Reddit user profiles
    - **youtube**: YouTube channel profiles
    """
    scraper = get_platform_scraper(request.platform)

    try:
        profile = await scraper.scrape_profile(request.username)
        if profile:
            return {
                "success": True,
                "data": profile.to_dict()
            }
        else:
            return {
                "success": False,
                "error": "Profile not found or is private",
                "platform": request.platform,
                "username": request.username
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Posts Endpoints ---

@router.post("/posts", summary="Scrape posts from a user")
async def scrape_posts(request: PostsRequest) -> Dict[str, Any]:
    """
    Scrape recent posts/content from a user on a social media platform.

    Returns a list of posts with engagement metrics.
    """
    scraper = get_platform_scraper(request.platform)

    try:
        posts = await scraper.scrape_posts(request.username, request.limit)
        return {
            "success": True,
            "count": len(posts),
            "data": [post.to_dict() for post in posts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Search Endpoints ---

@router.post("/search", summary="Search posts on a platform")
async def search_posts(request: SearchRequest) -> Dict[str, Any]:
    """
    Search for posts by keyword or hashtag on a social media platform.

    For Instagram, use hashtags (with or without #).
    For Twitter, supports keywords and hashtags.
    """
    scraper = get_platform_scraper(request.platform)

    try:
        posts = await scraper.search_posts(request.query, request.limit)
        return {
            "success": True,
            "query": request.query,
            "count": len(posts),
            "data": [post.to_dict() for post in posts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Generic URL Scraping ---

@router.post("/url", summary="Scrape any URL")
async def scrape_url(request: UrlScrapeRequest) -> Dict[str, Any]:
    """
    Scrape content from any URL using the specified engine.

    - **beautifulsoup**: Fast, for static HTML pages
    - **selenium**: For JavaScript-rendered pages (slower)
    - **playwright**: Modern async scraping (recommended for dynamic content)
    """
    scraper = get_engine_scraper(request.engine)

    try:
        if request.engine == ScraperEngine.PLAYWRIGHT and request.wait_selector:
            result = await scraper.scrape_url(request.url, wait_selector=request.wait_selector)
        else:
            result = await scraper.scrape_url(request.url)

        return {
            "success": "error" not in result,
            "engine": request.engine,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Article Scraping ---

@router.post("/article", summary="Scrape article content")
async def scrape_article(request: ArticleScrapeRequest) -> Dict[str, Any]:
    """
    Extract article content from a news or blog URL.
    Uses heuristics to find main article text.
    """
    scraper = BeautifulSoupScraper()

    try:
        result = await scraper.scrape_article(request.url)
        return {
            "success": "error" not in result,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Platform-Specific Endpoints ---

@router.post("/reddit/subreddit", summary="Scrape a subreddit")
async def scrape_subreddit(request: SubredditRequest) -> Dict[str, Any]:
    """
    Scrape posts from a subreddit.

    Sort options: hot, new, top, rising
    """
    scraper = RedditScraper()

    try:
        posts = await scraper.scrape_subreddit(request.subreddit, request.sort, request.limit)
        return {
            "success": True,
            "subreddit": request.subreddit,
            "sort": request.sort,
            "count": len(posts),
            "data": [post.to_dict() for post in posts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


@router.get("/reddit/subreddit/{subreddit}/info", summary="Get subreddit info")
async def get_subreddit_info(subreddit: str) -> Dict[str, Any]:
    """Get information about a subreddit."""
    scraper = RedditScraper()

    try:
        result = await scraper.scrape_subreddit_info(subreddit)
        return {
            "success": "error" not in result,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


@router.post("/youtube/video", summary="Scrape YouTube video details")
async def scrape_youtube_video(request: YouTubeVideoRequest) -> Dict[str, Any]:
    """
    Get details about a YouTube video.

    Provide the 11-character video ID (from URL: ?v=VIDEO_ID)
    """
    scraper = YouTubeScraper()

    try:
        result = await scraper.scrape_video(request.video_id)
        return {
            "success": "error" not in result,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


@router.post("/linkedin/company/{company_slug}", summary="Scrape LinkedIn company page")
async def scrape_linkedin_company(company_slug: str) -> Dict[str, Any]:
    """Get information about a LinkedIn company page."""
    scraper = LinkedInScraper()

    try:
        result = await scraper.scrape_company(company_slug)
        return {
            "success": "error" not in result,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Batch Scraping ---

class BatchProfileRequest(BaseModel):
    profiles: List[ProfileRequest] = Field(..., description="List of profiles to scrape")


@router.post("/batch/profiles", summary="Batch scrape multiple profiles")
async def batch_scrape_profiles(request: BatchProfileRequest) -> Dict[str, Any]:
    """
    Scrape multiple profiles in parallel.
    Maximum 10 profiles per request.
    """
    if len(request.profiles) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 profiles per batch request")

    results = []

    async def scrape_single(profile_req: ProfileRequest):
        scraper = get_platform_scraper(profile_req.platform)
        try:
            profile = await scraper.scrape_profile(profile_req.username)
            return {
                "platform": profile_req.platform,
                "username": profile_req.username,
                "success": profile is not None,
                "data": profile.to_dict() if profile else None
            }
        except Exception as e:
            return {
                "platform": profile_req.platform,
                "username": profile_req.username,
                "success": False,
                "error": str(e)
            }
        finally:
            await scraper.close()

    # Run all scrapes in parallel
    results = await asyncio.gather(*[scrape_single(p) for p in request.profiles])

    return {
        "success": True,
        "total": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "data": results
    }


# --- Screenshot Endpoint ---

class ScreenshotRequest(BaseModel):
    url: str = Field(..., description="URL to screenshot")
    full_page: bool = Field(default=True, description="Capture full page")


@router.post("/screenshot", summary="Take a screenshot of a webpage")
async def take_screenshot(request: ScreenshotRequest) -> Dict[str, Any]:
    """
    Take a screenshot of a webpage.
    Returns the screenshot as a base64 encoded image.
    """
    import base64
    import tempfile
    import os

    scraper = PlaywrightScraper()

    try:
        # Create temporary file for screenshot
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        success = await scraper.take_screenshot(request.url, tmp_path, request.full_page)

        if success and os.path.exists(tmp_path):
            with open(tmp_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            os.unlink(tmp_path)

            return {
                "success": True,
                "url": request.url,
                "image": f"data:image/png;base64,{image_data}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to take screenshot"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# --- Health Check ---

@router.get("/health", summary="Check scraping service health")
async def scraping_health() -> Dict[str, Any]:
    """Check if the scraping service is operational."""
    return {
        "status": "ok",
        "available_platforms": [p.value for p in Platform],
        "available_engines": [e.value for e in ScraperEngine]
    }
