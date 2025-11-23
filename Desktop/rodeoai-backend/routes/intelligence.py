"""
Intelligence API Routes
Deep user analysis, social graphs, political leaning, brand affinity endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.intelligence import (
    get_intelligence_service,
    PoliticalAnalyzer,
    BrandAffinityAnalyzer
)

router = APIRouter(prefix="/api/intel", tags=["intelligence"])


# --- Request Models ---

class UserAnalysisRequest(BaseModel):
    platform: str = Field(..., description="twitter, instagram, reddit, youtube")
    username: str = Field(..., description="Target username")
    depth: str = Field(default="standard", description="light, standard, or deep")


class MultiUserAnalysisRequest(BaseModel):
    platform: str
    usernames: List[str] = Field(..., max_items=50)
    depth: str = Field(default="light")


class SocialGraphRequest(BaseModel):
    platform: str
    username: str
    depth: int = Field(default=1, ge=1, le=2, description="Network depth (1 or 2)")


class FollowersRequest(BaseModel):
    platform: str
    username: str
    limit: int = Field(default=500, ge=1, le=5000)


class CompareUsersRequest(BaseModel):
    platform: str
    usernames: List[str] = Field(..., min_items=2, max_items=10)


class ContentAnalysisRequest(BaseModel):
    posts: List[Dict] = Field(..., description="List of posts with 'content' field")
    include_political: bool = True
    include_sentiment: bool = True
    include_brands: bool = True


# --- Analysis Endpoints ---

@router.post("/analyze", summary="Deep user analysis")
async def analyze_user(request: UserAnalysisRequest) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on a user including:
    - Profile information
    - Engagement patterns
    - Political leaning
    - Brand affinities
    - Demographic inferences
    - Personality traits
    - Interests and topics
    """
    service = get_intelligence_service()

    try:
        intel = await service.analyze_user(
            request.platform,
            request.username,
            request.depth
        )

        return {
            "success": True,
            "analysis_depth": request.depth,
            "data": intel.to_dict()
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/analyze/batch", summary="Batch user analysis")
async def analyze_users_batch(request: MultiUserAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze multiple users and return individual profiles.
    """
    service = get_intelligence_service()
    results = []

    for username in request.usernames:
        try:
            intel = await service.analyze_user(
                request.platform,
                username,
                request.depth
            )
            results.append({
                "username": username,
                "success": True,
                "data": intel.to_dict()
            })
        except Exception as e:
            results.append({
                "username": username,
                "success": False,
                "error": str(e)
            })

    return {
        "total": len(request.usernames),
        "successful": sum(1 for r in results if r["success"]),
        "results": results
    }


@router.post("/compare", summary="Compare multiple users")
async def compare_users(request: CompareUsersRequest) -> Dict[str, Any]:
    """
    Compare multiple users and find commonalities:
    - Common interests
    - Common brands followed
    - Political distribution
    """
    service = get_intelligence_service()

    try:
        comparison = await service.compare_users(
            request.platform,
            request.usernames
        )

        return {
            "success": True,
            **comparison
        }
    except Exception as e:
        raise HTTPException(500, str(e))


# --- Social Graph Endpoints ---

@router.post("/social-graph", summary="Build social graph")
async def build_social_graph(request: SocialGraphRequest) -> Dict[str, Any]:
    """
    Build a social graph showing:
    - Followers
    - Following
    - Mutual connections
    - Extended network (depth 2)
    """
    service = get_intelligence_service()

    try:
        graph = await service.build_social_graph(
            request.platform,
            request.username,
            request.depth
        )

        return {
            "success": True,
            "data": graph.to_dict()
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/followers", summary="Get followers list")
async def get_followers(request: FollowersRequest) -> Dict[str, Any]:
    """
    Get a user's followers list with categorization.
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    try:
        followers = await scraper.scrape_followers(
            request.platform,
            request.username,
            request.limit
        )

        categories = scraper.categorize_accounts(followers)

        return {
            "success": True,
            "username": request.username,
            "total_scraped": len(followers),
            "followers": followers,
            "categorized": categories
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/following", summary="Get following list")
async def get_following(request: FollowersRequest) -> Dict[str, Any]:
    """
    Get who a user follows with categorization into:
    - Brands
    - Media outlets
    - Politicians
    - Influencers
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    try:
        following = await scraper.scrape_following(
            request.platform,
            request.username,
            request.limit
        )

        categories = scraper.categorize_accounts(following)

        return {
            "success": True,
            "username": request.username,
            "total_scraped": len(following),
            "following": following,
            "categorized": categories,
            "brands_followed": categories["brands"],
            "media_followed": categories["media"],
            "politicians_followed": categories["politicians"]
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/following/{platform}/{username}/brands", summary="Get brands a user follows")
async def get_followed_brands(
    platform: str,
    username: str,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Get just the brands a user follows.
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    try:
        following = await scraper.scrape_following(platform, username, limit)
        categories = scraper.categorize_accounts(following)

        return {
            "success": True,
            "username": username,
            "brands": categories["brands"],
            "brand_count": len(categories["brands"])
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/following/{platform}/{username}/politicians", summary="Get politicians a user follows")
async def get_followed_politicians(
    platform: str,
    username: str,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Get politicians and political accounts a user follows.
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    try:
        following = await scraper.scrape_following(platform, username, limit)
        categories = scraper.categorize_accounts(following)

        return {
            "success": True,
            "username": username,
            "politicians": categories["politicians"],
            "count": len(categories["politicians"])
        }
    except Exception as e:
        raise HTTPException(500, str(e))


# --- Political Analysis Endpoints ---

@router.post("/political", summary="Analyze political leaning")
async def analyze_political(request: UserAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze a user's political leaning based on:
    - Content they post
    - Accounts they follow
    - Media outlets they engage with
    - Political keywords used

    Returns:
    - leaning: left, center-left, center, center-right, right
    - confidence: 0-1
    - indicators: list of detected signals
    """
    service = get_intelligence_service()

    # Get posts and following
    profile_data, posts = await service._get_base_data(
        request.platform,
        request.username,
        "standard"
    )

    following = []
    if request.depth != "light":
        following_data = await service.engagement_scraper.scrape_following(
            request.platform,
            request.username,
            500
        )
        following = following_data

    bio = profile_data.get("bio", "") if profile_data else ""

    # Analyze
    analyzer = PoliticalAnalyzer()
    result = analyzer.analyze_political_leaning(posts, following, bio)

    return {
        "success": True,
        "username": request.username,
        "platform": request.platform,
        "posts_analyzed": len(posts),
        "following_analyzed": len(following),
        **result
    }


@router.post("/political/batch", summary="Batch political analysis")
async def analyze_political_batch(request: MultiUserAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze political leaning for multiple users.
    Returns distribution across the political spectrum.
    """
    results = []
    distribution = {
        "left": 0,
        "center-left": 0,
        "center": 0,
        "center-right": 0,
        "right": 0,
        "unknown": 0
    }

    service = get_intelligence_service()
    analyzer = PoliticalAnalyzer()

    for username in request.usernames:
        try:
            profile_data, posts = await service._get_base_data(
                request.platform,
                username,
                "light"
            )

            bio = profile_data.get("bio", "") if profile_data else ""
            result = analyzer.analyze_political_leaning(posts, [], bio)

            leaning = result["leaning"]
            distribution[leaning] = distribution.get(leaning, 0) + 1

            results.append({
                "username": username,
                "leaning": leaning,
                "confidence": result["confidence"]
            })
        except Exception as e:
            results.append({
                "username": username,
                "error": str(e)
            })
            distribution["unknown"] += 1

    return {
        "total_analyzed": len(results),
        "distribution": distribution,
        "results": results
    }


# --- Brand Analysis Endpoints ---

@router.post("/brands", summary="Analyze brand affinities")
async def analyze_brands(request: UserAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze what brands a user engages with and their brand preferences.
    """
    service = get_intelligence_service()

    profile_data, posts = await service._get_base_data(
        request.platform,
        request.username,
        "standard"
    )

    following = []
    if request.depth != "light":
        following = await service.engagement_scraper.scrape_following(
            request.platform,
            request.username,
            500
        )

    analyzer = BrandAffinityAnalyzer()
    result = analyzer.analyze_brand_affinity(posts, following)

    return {
        "success": True,
        "username": request.username,
        **result
    }


# --- Content Analysis Endpoints ---

@router.post("/analyze/content", summary="Analyze content directly")
async def analyze_content(request: ContentAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze provided content without scraping.
    Useful for analyzing content you already have.
    """
    results = {}

    if request.include_political:
        analyzer = PoliticalAnalyzer()
        results["political"] = analyzer.analyze_political_leaning(request.posts, [], "")
        results["sentiment"] = analyzer.analyze_sentiment(request.posts)

    if request.include_brands:
        analyzer = BrandAffinityAnalyzer()
        results["brands"] = analyzer.analyze_brand_affinity(request.posts, [])

    return {
        "success": True,
        "posts_analyzed": len(request.posts),
        **results
    }


# --- Network Analysis Endpoints ---

@router.post("/network/influencers", summary="Find influencers in network")
async def find_network_influencers(
    request: UserAnalysisRequest,
    min_followers: int = 10000
) -> Dict[str, Any]:
    """
    Find influencers in a user's network (people they follow with high follower counts).
    """
    service = get_intelligence_service()

    try:
        influencers = await service.find_influencers_in_network(
            request.platform,
            request.username,
            min_followers
        )

        return {
            "success": True,
            "username": request.username,
            "influencers_found": len(influencers),
            "influencers": influencers
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/network/overlap", summary="Find follower overlap")
async def find_follower_overlap(request: CompareUsersRequest) -> Dict[str, Any]:
    """
    Find followers that multiple users have in common.
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    all_followers = {}
    for username in request.usernames:
        try:
            followers = await scraper.scrape_followers(
                request.platform,
                username,
                500
            )
            all_followers[username] = set(followers)
        except:
            all_followers[username] = set()

    # Find overlap
    if len(all_followers) >= 2:
        sets = list(all_followers.values())
        common = sets[0]
        for s in sets[1:]:
            common = common & s
    else:
        common = set()

    return {
        "success": True,
        "users_compared": request.usernames,
        "common_followers": list(common)[:500],
        "common_count": len(common),
        "individual_counts": {u: len(f) for u, f in all_followers.items()}
    }


# --- Hidden Insights Endpoints ---

@router.post("/demographics", summary="Infer demographics")
async def infer_demographics(request: UserAnalysisRequest) -> Dict[str, Any]:
    """
    Infer demographic information from user content:
    - Age range
    - Gender
    - Occupation
    - Location hints
    """
    from services.intelligence import HiddenDataExtractor

    service = get_intelligence_service()
    extractor = HiddenDataExtractor()

    profile_data, posts = await service._get_base_data(
        request.platform,
        request.username,
        "standard"
    )

    bio = profile_data.get("bio", "") if profile_data else ""
    display_name = profile_data.get("display_name", "") if profile_data else ""

    demographics = extractor.extract_demographics(bio, posts, display_name)
    personality = extractor.extract_personality_traits(posts)
    location = extractor.extract_location_hints(bio, posts)

    return {
        "success": True,
        "username": request.username,
        "demographics": demographics,
        "personality_traits": personality,
        "location_hints": location
    }


# --- Health Check ---

@router.get("/health", summary="Intelligence service health")
async def intel_health() -> Dict[str, Any]:
    """Check intelligence service status."""
    return {
        "status": "ok",
        "capabilities": [
            "user_analysis",
            "political_leaning",
            "brand_affinity",
            "social_graph",
            "demographic_inference",
            "network_analysis"
        ]
    }
