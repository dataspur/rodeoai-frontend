"""
Western Intelligence API Routes
Specialized endpoints for western wear, rodeo, and cowboy culture analysis.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/western", tags=["western"])


# --- Request Models ---

class WesternUserRequest(BaseModel):
    platform: str = Field(..., description="twitter, instagram")
    username: str = Field(..., description="Target username")


class BrandAnalysisRequest(BaseModel):
    platform: str
    brand_handle: str = Field(..., description="Brand's social handle")
    competitor_handles: List[str] = Field(default=[], max_items=10)


class InfluencerSearchRequest(BaseModel):
    platform: str = Field(default="instagram")
    category: str = Field(default="all", description="all, team_roping, bull_riding, barrel_racing, bronc_riding, lifestyle")
    min_followers: int = Field(default=5000)
    limit: int = Field(default=50, le=200)


class AudienceOverlapRequest(BaseModel):
    platform: str
    brand_handles: List[str] = Field(..., min_items=2, max_items=5)
    sample_size: int = Field(default=1000, le=5000)


class EventTrackingRequest(BaseModel):
    event_name: str = Field(..., description="nfr, pbr_world_finals, houston, san_antonio, cheyenne, calgary, pendleton")
    hashtags: List[str] = Field(default=[])
    date_range_days: int = Field(default=7, le=30)


# --- Western Brand Categories ---

WESTERN_CATEGORIES = {
    "boots": {
        "premium": ["lucchese", "tecovas", "andersonbean", "oldgringoboots"],
        "mainstream": ["ariat", "justinboots", "tonylamaboots", "corralboots", "danhpost"],
        "value": ["laredo", "durango", "twistex"]
    },
    "hats": {
        "premium": ["americanhatco", "prohats", "greeley", "serratelli"],
        "mainstream": ["resistol", "stetson", "atwood", "baileywestern"],
        "value": ["rodeoking", "bullhide", "charliehorse"]
    },
    "apparel": {
        "premium": ["txstandard", "texasstandard", "doubledranchwear", "manready"],
        "mainstream": ["wrangler", "cinch", "panhandleslim", "hooey"],
        "value": ["roper", "rockymountainclothing", "scully"]
    },
    "retailers": {
        "national": ["cavenders", "bootbarn", "sheplers"],
        "regional": ["drysdales", "millerranch"]
    },
    "equipment": {
        "saddles": ["martinsaddlery", "billcooksaddlery", "circley"],
        "ropes": ["classicropes", "cactusropes", "topropes", "rattler", "lonestarropes"]
    }
}

RODEO_EVENTS = {
    "nfr": {
        "name": "Wrangler National Finals Rodeo",
        "hashtags": ["#nfr", "#wranglernfr", "#nfr2024", "#lasvegasrodeo"],
        "location": "Las Vegas, NV",
        "month": "December"
    },
    "pbr_world_finals": {
        "name": "PBR World Finals",
        "hashtags": ["#pbr", "#pbrworldfinals", "#bullriding"],
        "location": "Fort Worth, TX",
        "month": "May"
    },
    "houston": {
        "name": "Houston Livestock Show & Rodeo",
        "hashtags": ["#rodeohouston", "#hlsr", "#houstonrodeo"],
        "location": "Houston, TX",
        "month": "March"
    },
    "san_antonio": {
        "name": "San Antonio Stock Show & Rodeo",
        "hashtags": ["#sarodeo", "#sanantoniostockshow"],
        "location": "San Antonio, TX",
        "month": "February"
    },
    "cheyenne": {
        "name": "Cheyenne Frontier Days",
        "hashtags": ["#cfd", "#cheyennefrontierdays", "#daddyofemal"],
        "location": "Cheyenne, WY",
        "month": "July"
    },
    "calgary": {
        "name": "Calgary Stampede",
        "hashtags": ["#calgarystampede", "#stampede"],
        "location": "Calgary, AB",
        "month": "July"
    },
    "pendleton": {
        "name": "Pendleton Round-Up",
        "hashtags": ["#pendletonroundup", "#leterduck"],
        "location": "Pendleton, OR",
        "month": "September"
    }
}

WESTERN_INFLUENCER_TIERS = {
    "mega": {"min_followers": 500000, "label": "Mega Influencer"},
    "macro": {"min_followers": 100000, "label": "Macro Influencer"},
    "mid": {"min_followers": 25000, "label": "Mid-Tier Influencer"},
    "micro": {"min_followers": 5000, "label": "Micro Influencer"},
    "nano": {"min_followers": 1000, "label": "Nano Influencer"}
}


# --- Western Profile Analysis ---

@router.post("/analyze", summary="Western-focused user analysis")
async def analyze_western_user(request: WesternUserRequest) -> Dict[str, Any]:
    """
    Analyze a user's western wear preferences and rodeo engagement.
    Returns:
    - Western brands followed
    - Rodeo events engaged with
    - Western influencers in network
    - Cowboy culture score (0-100)
    """
    from services.intelligence import get_intelligence_service, EngagementScraper, BrandAffinityAnalyzer

    service = get_intelligence_service()
    scraper = EngagementScraper()
    analyzer = BrandAffinityAnalyzer()

    try:
        # Get following list
        following = await scraper.scrape_following(
            request.platform,
            request.username,
            1000
        )

        # Get posts
        profile_data, posts = await service._get_base_data(
            request.platform,
            request.username,
            "standard"
        )

        # Categorize western brands
        western_brands = {
            "boots": [],
            "hats": [],
            "apparel": [],
            "retailers": [],
            "equipment": [],
            "events": [],
            "lifestyle": []
        }

        for account in following:
            account_lower = account.lower()
            # Check each category
            for cat, tiers in WESTERN_CATEGORIES.items():
                for tier, brands in tiers.items():
                    if account_lower in brands:
                        western_brands[cat].append({
                            "brand": account,
                            "tier": tier
                        })

        # Check for rodeo events
        event_follows = []
        for account in following:
            account_lower = account.lower()
            for event_key, event_data in RODEO_EVENTS.items():
                if event_key in account_lower or any(tag.replace("#", "") in account_lower for tag in event_data["hashtags"]):
                    event_follows.append(event_data["name"])

        # Check western influencers in network
        from services.intelligence.extraction import BrandAffinityAnalyzer as BA
        western_influencers_followed = []
        for account in following:
            if account.lower() in BA.WESTERN_INFLUENCERS:
                western_influencers_followed.append(account)

        # Analyze posts for western content
        western_hashtags = []
        western_keywords = ["rodeo", "cowboy", "western", "ranch", "boots", "wrangler", "nfr", "pbr", "roping", "barrel"]
        western_content_count = 0

        for post in posts:
            content = post.get("content", "").lower()
            if any(kw in content for kw in western_keywords):
                western_content_count += 1
            # Extract western hashtags
            import re
            hashtags = re.findall(r"#(\w+)", content)
            for tag in hashtags:
                if any(kw in tag.lower() for kw in western_keywords):
                    western_hashtags.append(tag)

        # Calculate cowboy culture score (0-100)
        score = 0
        score += min(len(western_brands["boots"]) * 5, 15)
        score += min(len(western_brands["hats"]) * 5, 15)
        score += min(len(western_brands["apparel"]) * 3, 15)
        score += min(len(western_brands["retailers"]) * 5, 10)
        score += min(len(event_follows) * 5, 15)
        score += min(len(western_influencers_followed) * 2, 10)
        score += min(western_content_count, 20)

        return {
            "success": True,
            "username": request.username,
            "platform": request.platform,
            "cowboy_culture_score": min(score, 100),
            "western_brands_followed": western_brands,
            "total_western_brands": sum(len(v) for v in western_brands.values()),
            "rodeo_events_followed": list(set(event_follows)),
            "western_influencers_followed": western_influencers_followed,
            "western_hashtags_used": list(set(western_hashtags))[:50],
            "western_content_percentage": round(western_content_count / max(len(posts), 1) * 100, 1),
            "posts_analyzed": len(posts),
            "following_analyzed": len(following)
        }

    except Exception as e:
        raise HTTPException(500, str(e))


# --- Brand Competitor Analysis ---

@router.post("/brand/analyze", summary="Analyze western brand")
async def analyze_western_brand(request: BrandAnalysisRequest) -> Dict[str, Any]:
    """
    Deep analysis of a western brand's social presence:
    - Follower demographics
    - Engagement rates
    - Influencer partnerships
    - Competitor comparison
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    try:
        # Get brand followers
        brand_followers = await scraper.scrape_followers(
            request.platform,
            request.brand_handle,
            2000
        )

        # Categorize brand followers
        categories = scraper.categorize_accounts(brand_followers)

        # Get competitor data if provided
        competitor_data = {}
        for comp in request.competitor_handles[:5]:
            try:
                comp_followers = await scraper.scrape_followers(
                    request.platform,
                    comp,
                    1000
                )
                # Find overlap
                overlap = set(brand_followers) & set(comp_followers)
                competitor_data[comp] = {
                    "follower_count": len(comp_followers),
                    "overlap_with_brand": len(overlap),
                    "overlap_percentage": round(len(overlap) / max(len(brand_followers), 1) * 100, 1)
                }
            except:
                competitor_data[comp] = {"error": "Could not fetch"}

        # Identify influencer followers
        from services.intelligence.extraction import BrandAffinityAnalyzer as BA
        influencer_followers = []
        for follower in brand_followers:
            if follower.lower() in BA.WESTERN_INFLUENCERS:
                influencer_followers.append(follower)

        return {
            "success": True,
            "brand": request.brand_handle,
            "platform": request.platform,
            "total_followers_sampled": len(brand_followers),
            "follower_categories": categories,
            "influencers_following_brand": influencer_followers,
            "influencer_count": len(influencer_followers),
            "competitor_analysis": competitor_data
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/brand/competitors", summary="Compare brand competitors")
async def compare_brand_competitors(request: AudienceOverlapRequest) -> Dict[str, Any]:
    """
    Compare audience overlap between western brands.
    Useful for market positioning and partnership opportunities.
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    brand_data = {}
    for brand in request.brand_handles:
        try:
            followers = await scraper.scrape_followers(
                request.platform,
                brand,
                request.sample_size
            )
            brand_data[brand] = set(followers)
        except:
            brand_data[brand] = set()

    # Calculate pairwise overlaps
    overlaps = {}
    brands = list(brand_data.keys())
    for i, brand1 in enumerate(brands):
        for brand2 in brands[i+1:]:
            overlap = brand_data[brand1] & brand_data[brand2]
            key = f"{brand1}_vs_{brand2}"
            overlaps[key] = {
                "common_followers": len(overlap),
                "percentage_of_brand1": round(len(overlap) / max(len(brand_data[brand1]), 1) * 100, 1),
                "percentage_of_brand2": round(len(overlap) / max(len(brand_data[brand2]), 1) * 100, 1),
                "sample_common": list(overlap)[:20]
            }

    # Find followers unique to each brand
    unique_followers = {}
    for brand in brands:
        others = set()
        for other_brand, followers in brand_data.items():
            if other_brand != brand:
                others.update(followers)
        unique = brand_data[brand] - others
        unique_followers[brand] = {
            "unique_count": len(unique),
            "unique_percentage": round(len(unique) / max(len(brand_data[brand]), 1) * 100, 1)
        }

    return {
        "success": True,
        "brands_analyzed": brands,
        "sample_sizes": {b: len(f) for b, f in brand_data.items()},
        "pairwise_overlaps": overlaps,
        "unique_audiences": unique_followers
    }


# --- Influencer Discovery ---

@router.post("/influencers/discover", summary="Discover western influencers")
async def discover_western_influencers(request: InfluencerSearchRequest) -> Dict[str, Any]:
    """
    Discover western/rodeo influencers by category.
    Categories: team_roping, bull_riding, barrel_racing, bronc_riding, lifestyle
    """
    from services.intelligence.extraction import BrandAffinityAnalyzer as BA

    # Categorized influencers
    influencer_categories = {
        "team_roping": [
            "taborropin", "speedwilliams", "claywsmith", "trevorbrazilebrand",
            "kalubwray", "wesleyduby", "colemilligan", "tyleranderson"
        ],
        "bull_riding": [
            "jbmauney", "lockwood", "dallonkasel", "josetovito",
            "bushwacker", "sagejohnson", "kobyradley"
        ],
        "bronc_riding": [
            "wright_broncs", "russmetal", "zekethe", "jadecoutts"
        ],
        "barrel_racing": [
            "hailiekinsel", "brittanypozzi", "ivypconrado",
            "tianyehager", "shalielarsson"
        ],
        "lifestyle": [
            "tyemurray", "tyharris", "trevorbrazile", "rickysonnygreen"
        ]
    }

    if request.category == "all":
        selected = []
        for cat_influencers in influencer_categories.values():
            selected.extend(cat_influencers)
    else:
        selected = influencer_categories.get(request.category, [])

    # Get profile data for each influencer
    from services.scrapers import InstagramScraper, TwitterScraper

    scrapers = {
        "instagram": InstagramScraper,
        "twitter": TwitterScraper
    }

    scraper_class = scrapers.get(request.platform)
    if not scraper_class:
        raise HTTPException(400, "Platform must be instagram or twitter")

    influencer_profiles = []
    for handle in selected[:request.limit]:
        scraper = scraper_class()
        try:
            profile = await scraper.scrape_profile(handle)
            if profile and profile.followers >= request.min_followers:
                # Determine tier
                tier = "nano"
                for tier_name, tier_data in WESTERN_INFLUENCER_TIERS.items():
                    if profile.followers >= tier_data["min_followers"]:
                        tier = tier_name
                        break

                influencer_profiles.append({
                    "handle": handle,
                    "display_name": profile.display_name,
                    "followers": profile.followers,
                    "following": profile.following,
                    "tier": tier,
                    "tier_label": WESTERN_INFLUENCER_TIERS[tier]["label"],
                    "bio": profile.bio[:200] if profile.bio else "",
                    "verified": profile.verified,
                    "category": request.category if request.category != "all" else _get_influencer_category(handle, influencer_categories)
                })
        except:
            pass
        finally:
            await scraper.close()

    # Sort by followers
    influencer_profiles.sort(key=lambda x: x["followers"], reverse=True)

    return {
        "success": True,
        "category": request.category,
        "platform": request.platform,
        "min_followers": request.min_followers,
        "influencers_found": len(influencer_profiles),
        "influencers": influencer_profiles,
        "tier_breakdown": _count_tiers(influencer_profiles)
    }


def _get_influencer_category(handle: str, categories: Dict) -> str:
    for cat, handles in categories.items():
        if handle in handles:
            return cat
    return "unknown"


def _count_tiers(profiles: List[Dict]) -> Dict[str, int]:
    tiers = {}
    for p in profiles:
        tier = p.get("tier", "unknown")
        tiers[tier] = tiers.get(tier, 0) + 1
    return tiers


@router.post("/influencers/score", summary="Score an influencer")
async def score_western_influencer(request: WesternUserRequest) -> Dict[str, Any]:
    """
    Calculate an influence score for a western/rodeo personality.
    Factors: followers, engagement, brand partnerships, content quality.
    """
    from services.intelligence import get_intelligence_service, EngagementScraper
    from services.scrapers import InstagramScraper, TwitterScraper

    scrapers = {
        "instagram": InstagramScraper,
        "twitter": TwitterScraper
    }

    scraper_class = scrapers.get(request.platform)
    if not scraper_class:
        raise HTTPException(400, "Platform must be instagram or twitter")

    scraper = scraper_class()
    service = get_intelligence_service()

    try:
        # Get profile
        profile = await scraper.scrape_profile(request.username)
        if not profile:
            raise HTTPException(404, "Profile not found")

        # Get posts
        posts = await scraper.scrape_posts(request.username, 50)

        # Calculate engagement rate
        total_engagement = sum(p.likes + p.comments for p in posts if p.likes and p.comments)
        avg_engagement = total_engagement / max(len(posts), 1)
        engagement_rate = (avg_engagement / max(profile.followers, 1)) * 100

        # Check brand mentions in posts
        from services.intelligence.extraction import EngagementScraper as ES
        brand_mentions = []
        for post in posts:
            content = post.content.lower() if post.content else ""
            for brand in ES.KNOWN_BRANDS:
                if brand in content or f"@{brand}" in content:
                    brand_mentions.append(brand)

        # Calculate influence score (0-100)
        score = 0

        # Follower score (0-30)
        if profile.followers >= 500000:
            score += 30
        elif profile.followers >= 100000:
            score += 25
        elif profile.followers >= 50000:
            score += 20
        elif profile.followers >= 10000:
            score += 15
        elif profile.followers >= 5000:
            score += 10
        else:
            score += 5

        # Engagement score (0-30)
        if engagement_rate >= 5:
            score += 30
        elif engagement_rate >= 3:
            score += 25
        elif engagement_rate >= 2:
            score += 20
        elif engagement_rate >= 1:
            score += 15
        else:
            score += 10

        # Brand partnership score (0-20)
        unique_brands = len(set(brand_mentions))
        score += min(unique_brands * 4, 20)

        # Verification bonus (0-10)
        if profile.verified:
            score += 10

        # Content consistency (0-10)
        if len(posts) >= 40:
            score += 10
        elif len(posts) >= 20:
            score += 5

        # Determine tier
        tier = "nano"
        for tier_name, tier_data in WESTERN_INFLUENCER_TIERS.items():
            if profile.followers >= tier_data["min_followers"]:
                tier = tier_name
                break

        return {
            "success": True,
            "username": request.username,
            "platform": request.platform,
            "influence_score": min(score, 100),
            "tier": tier,
            "tier_label": WESTERN_INFLUENCER_TIERS[tier]["label"],
            "metrics": {
                "followers": profile.followers,
                "following": profile.following,
                "posts_analyzed": len(posts),
                "avg_engagement": round(avg_engagement, 1),
                "engagement_rate": round(engagement_rate, 2),
                "verified": profile.verified
            },
            "brand_partnerships_detected": list(set(brand_mentions)),
            "partnership_count": len(set(brand_mentions)),
            "score_breakdown": {
                "follower_score": "/30",
                "engagement_score": "/30",
                "brand_score": "/20",
                "verification_bonus": "/10",
                "content_score": "/10"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


# --- Rodeo Event Tracking ---

@router.post("/events/track", summary="Track rodeo event engagement")
async def track_rodeo_event(request: EventTrackingRequest) -> Dict[str, Any]:
    """
    Track social media engagement around rodeo events.
    Returns trending hashtags, top posts, brand mentions.
    """
    event_data = RODEO_EVENTS.get(request.event_name)
    if not event_data:
        raise HTTPException(400, f"Unknown event. Valid events: {list(RODEO_EVENTS.keys())}")

    # Combine event hashtags with custom ones
    all_hashtags = list(set(event_data["hashtags"] + request.hashtags))

    return {
        "success": True,
        "event": event_data["name"],
        "location": event_data["location"],
        "typical_month": event_data["month"],
        "tracking_hashtags": all_hashtags,
        "tracking_duration_days": request.date_range_days,
        "message": "Event tracking initiated. Use /api/bulk/hashtag to scrape posts with these hashtags."
    }


@router.get("/events", summary="List rodeo events")
async def list_rodeo_events() -> Dict[str, Any]:
    """Get list of major rodeo events and their details."""
    return {
        "success": True,
        "events": RODEO_EVENTS,
        "total_events": len(RODEO_EVENTS)
    }


# --- Market Intelligence ---

@router.get("/categories", summary="Get western brand categories")
async def get_western_categories() -> Dict[str, Any]:
    """Get all western brand categories and tiers."""
    return {
        "success": True,
        "categories": WESTERN_CATEGORIES,
        "influencer_tiers": WESTERN_INFLUENCER_TIERS
    }


@router.post("/market/segment", summary="Segment user by western market")
async def segment_western_market(request: WesternUserRequest) -> Dict[str, Any]:
    """
    Segment a user into western market categories:
    - Premium Cowboy: Follows luxury western brands
    - Working Ranch: Practical/functional focus
    - Rodeo Enthusiast: Event and competition focused
    - Western Lifestyle: Fashion/aesthetic focus
    - Casual Western: Light engagement
    """
    from services.intelligence import EngagementScraper

    scraper = EngagementScraper()

    try:
        following = await scraper.scrape_following(
            request.platform,
            request.username,
            500
        )

        following_lower = {f.lower() for f in following}

        # Score each segment
        segments = {
            "premium_cowboy": 0,
            "working_ranch": 0,
            "rodeo_enthusiast": 0,
            "western_lifestyle": 0,
            "casual_western": 0
        }

        # Premium brands
        premium_brands = set()
        for cat, tiers in WESTERN_CATEGORIES.items():
            if "premium" in tiers:
                premium_brands.update(tiers["premium"])

        for brand in premium_brands:
            if brand in following_lower:
                segments["premium_cowboy"] += 3

        # Working ranch (equipment, mainstream boots)
        working_brands = set(WESTERN_CATEGORIES["equipment"].get("saddles", []))
        working_brands.update(WESTERN_CATEGORIES["equipment"].get("ropes", []))
        working_brands.update(WESTERN_CATEGORIES["boots"].get("mainstream", []))

        for brand in working_brands:
            if brand in following_lower:
                segments["working_ranch"] += 2

        # Rodeo enthusiast (events, athletes)
        event_brands = ["prca", "prorodeo", "pbr", "nfrodeo", "wranglernfr"]
        from services.intelligence.extraction import BrandAffinityAnalyzer as BA

        for brand in event_brands:
            if brand in following_lower:
                segments["rodeo_enthusiast"] += 3

        for influencer in BA.WESTERN_INFLUENCERS:
            if influencer in following_lower:
                segments["rodeo_enthusiast"] += 1

        # Western lifestyle (fashion brands, yellowstone)
        lifestyle_brands = ["yellowstone", "yellowstonetv", "1883", "1923", "yeti", "traeger"]
        lifestyle_brands.extend(WESTERN_CATEGORIES["apparel"].get("premium", []))

        for brand in lifestyle_brands:
            if brand in following_lower:
                segments["western_lifestyle"] += 2

        # Casual (retailers, value brands)
        casual_brands = WESTERN_CATEGORIES["retailers"].get("national", [])
        for cat in WESTERN_CATEGORIES.values():
            if isinstance(cat, dict) and "value" in cat:
                casual_brands.extend(cat["value"])

        for brand in casual_brands:
            if brand in following_lower:
                segments["casual_western"] += 1

        # Determine primary segment
        primary_segment = max(segments, key=segments.get)
        total_score = sum(segments.values())

        # If very low score, they're casual
        if total_score < 5:
            primary_segment = "casual_western"

        segment_descriptions = {
            "premium_cowboy": "High-end western wear enthusiast, values quality craftsmanship",
            "working_ranch": "Practical focus, real ranch/rodeo work, values durability",
            "rodeo_enthusiast": "Passionate about competitive rodeo, follows athletes and events",
            "western_lifestyle": "Fashion-forward western aesthetic, influenced by media",
            "casual_western": "Light western interest, occasional engagement"
        }

        return {
            "success": True,
            "username": request.username,
            "primary_segment": primary_segment,
            "segment_description": segment_descriptions[primary_segment],
            "segment_scores": segments,
            "total_western_score": total_score,
            "following_analyzed": len(following)
        }

    except Exception as e:
        raise HTTPException(500, str(e))


# --- Sponsored Content Detection ---

@router.post("/sponsored/detect", summary="Detect sponsored content")
async def detect_sponsored_content(request: WesternUserRequest) -> Dict[str, Any]:
    """
    Detect sponsored/paid content in a user's posts.
    Identifies:
    - FTC disclosure indicators (#ad, #sponsored, etc.)
    - Brand partnership hashtags (#teamwrangler, etc.)
    - Likely brand ambassador relationships
    """
    from services.intelligence import get_intelligence_service, SponsoredContentDetector

    service = get_intelligence_service()
    detector = SponsoredContentDetector()

    try:
        profile_data, posts = await service._get_base_data(
            request.platform,
            request.username,
            "deep"  # Get more posts for better detection
        )

        result = detector.detect_sponsored_content(posts)

        return {
            "success": True,
            "username": request.username,
            "platform": request.platform,
            **result
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/sponsored/value", summary="Estimate partnership value")
async def estimate_partnership_value(request: WesternUserRequest) -> Dict[str, Any]:
    """
    Estimate the partnership/sponsorship value for an influencer.
    Returns estimated CPM, post value, and partnership tier.
    """
    from services.intelligence import get_intelligence_service, SponsoredContentDetector
    from services.scrapers import InstagramScraper, TwitterScraper

    scrapers = {
        "instagram": InstagramScraper,
        "twitter": TwitterScraper
    }

    scraper_class = scrapers.get(request.platform)
    if not scraper_class:
        raise HTTPException(400, "Platform must be instagram or twitter")

    scraper = scraper_class()
    detector = SponsoredContentDetector()
    service = get_intelligence_service()

    try:
        # Get profile for follower count
        profile = await scraper.scrape_profile(request.username)
        if not profile:
            raise HTTPException(404, "Profile not found")

        # Get posts
        _, posts = await service._get_base_data(
            request.platform,
            request.username,
            "standard"
        )

        result = detector.analyze_partnership_value(posts, profile.followers)

        return {
            "success": True,
            "username": request.username,
            "platform": request.platform,
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


# --- Audience Persona Analysis ---

@router.post("/persona/build", summary="Build user persona")
async def build_user_persona(request: WesternUserRequest) -> Dict[str, Any]:
    """
    Build a western market persona for a user based on their content and following.
    Personas: ranch_hand, rodeo_competitor, western_fashion, country_lifestyle,
              yellowstone_fan, weekend_cowboy
    """
    from services.intelligence import get_intelligence_service, EngagementScraper, AudiencePersonaBuilder

    service = get_intelligence_service()
    scraper = EngagementScraper()
    builder = AudiencePersonaBuilder()

    try:
        # Get posts and following
        profile_data, posts = await service._get_base_data(
            request.platform,
            request.username,
            "standard"
        )

        following = await scraper.scrape_following(
            request.platform,
            request.username,
            500
        )

        bio = profile_data.get("bio", "") if profile_data else ""

        persona = builder.build_persona(posts, following, bio)

        return {
            "success": True,
            "username": request.username,
            "platform": request.platform,
            **persona,
            "posts_analyzed": len(posts),
            "following_analyzed": len(following)
        }

    except Exception as e:
        raise HTTPException(500, str(e))


class BatchPersonaRequest(BaseModel):
    platform: str
    usernames: List[str] = Field(..., max_items=50)


@router.post("/persona/batch", summary="Build personas for multiple users")
async def build_batch_personas(request: BatchPersonaRequest) -> Dict[str, Any]:
    """
    Build personas for multiple users and get audience segment distribution.
    """
    from services.intelligence import get_intelligence_service, EngagementScraper, AudiencePersonaBuilder

    service = get_intelligence_service()
    scraper = EngagementScraper()
    builder = AudiencePersonaBuilder()

    user_profiles = []
    results = []

    for username in request.usernames:
        try:
            profile_data, posts = await service._get_base_data(
                request.platform,
                username,
                "light"
            )

            following = await scraper.scrape_following(
                request.platform,
                username,
                100  # Smaller sample for batch
            )

            bio = profile_data.get("bio", "") if profile_data else ""

            persona = builder.build_persona(posts, following, bio)
            results.append({
                "username": username,
                "success": True,
                "persona": persona["primary_persona"],
                "description": persona["primary_description"]
            })

            user_profiles.append({
                "username": username,
                "posts": posts,
                "following": following,
                "bio": bio
            })

        except Exception as e:
            results.append({
                "username": username,
                "success": False,
                "error": str(e)
            })

    # Get overall segmentation
    segmentation = builder.segment_audience(user_profiles)

    return {
        "success": True,
        "total_users": len(request.usernames),
        "successful": sum(1 for r in results if r.get("success")),
        "results": results,
        "audience_segmentation": segmentation
    }


@router.get("/persona/templates", summary="Get persona templates")
async def get_persona_templates() -> Dict[str, Any]:
    """Get all available persona templates and their characteristics."""
    from services.intelligence import AudiencePersonaBuilder

    builder = AudiencePersonaBuilder()

    return {
        "success": True,
        "personas": builder.PERSONA_TEMPLATES
    }


# --- Health Check ---

@router.get("/health", summary="Western intelligence health")
async def western_health() -> Dict[str, Any]:
    """Check western intelligence service status."""
    return {
        "status": "ok",
        "capabilities": [
            "western_user_analysis",
            "brand_competitor_analysis",
            "influencer_discovery",
            "influencer_scoring",
            "rodeo_event_tracking",
            "market_segmentation",
            "sponsored_content_detection",
            "partnership_value_estimation",
            "audience_persona_building",
            "batch_persona_segmentation"
        ],
        "tracked_categories": list(WESTERN_CATEGORIES.keys()),
        "tracked_events": list(RODEO_EVENTS.keys())
    }
