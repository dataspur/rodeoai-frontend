"""
Western Data Scraping API Routes
E-commerce, competition, horse sales, pedigree, and social media data endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/data", tags=["western_data"])


# --- Request Models ---

class ProductSearchRequest(BaseModel):
    query: str
    source: str = Field(default="boot_barn", description="boot_barn, cavenders, ariat, wrangler, state_line_tack")
    limit: int = Field(default=50, le=200)


class CategoryScrapeRequest(BaseModel):
    source: str
    category: str
    limit: int = Field(default=100, le=500)


class CompetitionResultsRequest(BaseModel):
    association: str = Field(..., description="ncha or nrcha")
    year: int = Field(default=2024)
    division: Optional[str] = None
    event_id: Optional[str] = None


class StandingsRequest(BaseModel):
    association: str
    year: int
    division: str
    category: str = Field(default="rider", description="rider or horse")


class HorseSaleRequest(BaseModel):
    source: str = Field(default="heritage_place", description="heritage_place, wagonhound, rocking_p")
    year: Optional[int] = None
    sale_id: Optional[str] = None


class PedigreeRequest(BaseModel):
    horse_name: str
    include_offspring: bool = False


class ListingSearchRequest(BaseModel):
    discipline: str = Field(default="cutting")
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = Field(default=50, le=100)


# --- E-Commerce Endpoints ---

@router.post("/ecommerce/search", summary="Search western retail products")
async def search_products(request: ProductSearchRequest) -> Dict[str, Any]:
    """Search for products across western retail sites."""
    from services.scrapers.ecommerce import (
        BootBarnScraper, CavendersScraper, AriatScraper,
        WranglerScraper, StateLineTackScraper
    )

    scrapers = {
        "boot_barn": BootBarnScraper,
        "cavenders": CavendersScraper,
        "ariat": AriatScraper,
        "wrangler": WranglerScraper,
        "state_line_tack": StateLineTackScraper
    }

    scraper_class = scrapers.get(request.source)
    if not scraper_class:
        raise HTTPException(400, f"Invalid source. Options: {list(scrapers.keys())}")

    scraper = scraper_class()

    try:
        products = await scraper.search_products(request.query, request.limit)

        return {
            "success": True,
            "source": request.source,
            "query": request.query,
            "count": len(products),
            "products": [p.to_dict() for p in products]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.post("/ecommerce/category", summary="Scrape product category")
async def scrape_category(request: CategoryScrapeRequest) -> Dict[str, Any]:
    """Scrape all products from a category."""
    from services.scrapers.ecommerce import (
        BootBarnScraper, CavendersScraper, AriatScraper,
        WranglerScraper, StateLineTackScraper
    )

    scrapers = {
        "boot_barn": BootBarnScraper,
        "cavenders": CavendersScraper,
        "ariat": AriatScraper,
        "wrangler": WranglerScraper,
        "state_line_tack": StateLineTackScraper
    }

    scraper_class = scrapers.get(request.source)
    if not scraper_class:
        raise HTTPException(400, f"Invalid source")

    scraper = scraper_class()

    try:
        products = await scraper.scrape_category(request.category, request.limit)

        return {
            "success": True,
            "source": request.source,
            "category": request.category,
            "count": len(products),
            "products": [p.to_dict() for p in products]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.get("/ecommerce/sources", summary="List e-commerce sources")
async def list_ecommerce_sources() -> Dict[str, Any]:
    """Get available e-commerce sources and their categories."""
    from services.scrapers.ecommerce import (
        BootBarnScraper, CavendersScraper, AriatScraper,
        WranglerScraper, StateLineTackScraper
    )

    return {
        "success": True,
        "sources": {
            "boot_barn": {
                "name": "Boot Barn",
                "url": "https://www.bootbarn.com",
                "categories": list(BootBarnScraper.CATEGORIES.keys())
            },
            "cavenders": {
                "name": "Cavender's",
                "url": "https://www.cavenders.com",
                "categories": list(CavendersScraper.CATEGORIES.keys())
            },
            "ariat": {
                "name": "Ariat",
                "url": "https://www.ariat.com",
                "categories": list(AriatScraper.CATEGORIES.keys())
            },
            "wrangler": {
                "name": "Wrangler",
                "url": "https://www.wrangler.com",
                "categories": list(WranglerScraper.CATEGORIES.keys())
            },
            "state_line_tack": {
                "name": "State Line Tack",
                "url": "https://www.statelinetack.com",
                "categories": list(StateLineTackScraper.CATEGORIES.keys())
            }
        }
    }


# --- Competition Data Endpoints ---

@router.post("/competition/results", summary="Get competition results")
async def get_competition_results(request: CompetitionResultsRequest) -> Dict[str, Any]:
    """Get NCHA or NRCHA competition results."""
    from services.scrapers.competition import NCHAScraper, NRCHAScraper

    scrapers = {
        "ncha": NCHAScraper,
        "nrcha": NRCHAScraper
    }

    scraper_class = scrapers.get(request.association)
    if not scraper_class:
        raise HTTPException(400, "Association must be 'ncha' or 'nrcha'")

    scraper = scraper_class()

    try:
        results = await scraper.scrape_results(
            event_id=request.event_id,
            year=request.year,
            division=request.division
        )

        return {
            "success": True,
            "association": request.association,
            "year": request.year,
            "division": request.division,
            "count": len(results),
            "results": [r.to_dict() for r in results]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.post("/competition/standings", summary="Get standings/rankings")
async def get_standings(request: StandingsRequest) -> Dict[str, Any]:
    """Get year-end standings for NCHA or NRCHA."""
    from services.scrapers.competition import NCHAScraper, NRCHAScraper

    scrapers = {
        "ncha": NCHAScraper,
        "nrcha": NRCHAScraper
    }

    scraper_class = scrapers.get(request.association)
    if not scraper_class:
        raise HTTPException(400, "Association must be 'ncha' or 'nrcha'")

    scraper = scraper_class()

    try:
        standings = await scraper.scrape_standings(
            year=request.year,
            division=request.division,
            category=request.category
        )

        return {
            "success": True,
            "association": request.association,
            "year": request.year,
            "division": request.division,
            "category": request.category,
            "count": len(standings),
            "standings": [s.to_dict() for s in standings]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.get("/competition/events", summary="Get upcoming events")
async def get_competition_events(
    association: str = Query(..., description="ncha or nrcha")
) -> Dict[str, Any]:
    """Get upcoming competition events."""
    from services.scrapers.competition import NCHAScraper, NRCHAScraper

    scrapers = {
        "ncha": NCHAScraper,
        "nrcha": NRCHAScraper
    }

    scraper_class = scrapers.get(association)
    if not scraper_class:
        raise HTTPException(400, "Association must be 'ncha' or 'nrcha'")

    scraper = scraper_class()

    try:
        events = await scraper.scrape_events()

        return {
            "success": True,
            "association": association,
            "count": len(events),
            "events": [e.to_dict() for e in events]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.get("/competition/divisions", summary="List available divisions")
async def list_divisions() -> Dict[str, Any]:
    """Get available divisions for each association."""
    from services.scrapers.competition import NCHAScraper, NRCHAScraper

    return {
        "success": True,
        "divisions": {
            "ncha": NCHAScraper.DIVISIONS,
            "nrcha": NRCHAScraper.DIVISIONS
        }
    }


# --- Horse Sale Endpoints ---

@router.post("/sales/results", summary="Get horse sale results")
async def get_sale_results(request: HorseSaleRequest) -> Dict[str, Any]:
    """Get horse sale results from Heritage Place, ranch sales, etc."""
    from services.scrapers.horses import HorseSaleScraper

    scraper = HorseSaleScraper()

    try:
        if request.source == "heritage_place":
            results = await scraper.scrape_heritage_place(
                sale_id=request.sale_id,
                year=request.year
            )
        else:
            results = await scraper.scrape_ranch_sale(request.source)

        return {
            "success": True,
            "source": request.source,
            "count": len(results),
            "sales": [r.to_dict() for r in results]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.get("/sales/recent", summary="Get recent sales")
async def get_recent_sales(limit: int = 50) -> Dict[str, Any]:
    """Get most recent horse sale results across all sources."""
    from services.scrapers.horses import HorseSaleScraper

    scraper = HorseSaleScraper()

    try:
        results = await scraper.get_recent_sales(limit)

        return {
            "success": True,
            "count": len(results),
            "sales": [r.to_dict() for r in results]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


# --- Pedigree Endpoints ---

@router.post("/pedigree/lookup", summary="Look up horse pedigree")
async def lookup_pedigree(request: PedigreeRequest) -> Dict[str, Any]:
    """Look up pedigree information for a horse."""
    from services.scrapers.horses import PedigreeScraper

    scraper = PedigreeScraper()

    try:
        pedigree = await scraper.get_pedigree(request.horse_name)

        if not pedigree:
            raise HTTPException(404, "Horse not found")

        result = {
            "success": True,
            "pedigree": pedigree.to_dict()
        }

        if request.include_offspring:
            offspring = await scraper.get_offspring(request.horse_name)
            result["offspring"] = offspring

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.get("/pedigree/search", summary="Search horses")
async def search_horses(name: str = Query(..., min_length=2)) -> Dict[str, Any]:
    """Search for horses by name."""
    from services.scrapers.horses import PedigreeScraper

    scraper = PedigreeScraper()

    try:
        results = await scraper.search_horse(name)

        return {
            "success": True,
            "query": name,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


# --- Horse Listing Endpoints ---

@router.post("/listings/search", summary="Search horse listings")
async def search_listings(request: ListingSearchRequest) -> Dict[str, Any]:
    """Search for horses for sale."""
    from services.scrapers.horses import HorseListingScraper

    scraper = HorseListingScraper()

    try:
        if request.min_price or request.max_price:
            listings = await scraper.search_by_price_range(
                min_price=request.min_price or 0,
                max_price=request.max_price or 1000000,
                discipline=request.discipline,
                limit=request.limit
            )
        else:
            listings = await scraper.search_cutting_horses(request.limit)

        return {
            "success": True,
            "discipline": request.discipline,
            "count": len(listings),
            "listings": [l.to_dict() for l in listings]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


@router.get("/listings/prospects", summary="Get cutting prospects")
async def get_prospects(limit: int = 30) -> Dict[str, Any]:
    """Get cutting horse prospects for sale."""
    from services.scrapers.horses import HorseListingScraper

    scraper = HorseListingScraper()

    try:
        listings = await scraper.search_prospects(limit)

        return {
            "success": True,
            "count": len(listings),
            "listings": [l.to_dict() for l in listings]
        }

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        await scraper.close()


# --- Social Media Targets ---

@router.get("/social/targets", summary="Get social scraping targets")
async def get_social_targets() -> Dict[str, Any]:
    """Get all configured social media scraping targets."""
    from services.scrapers.social_targets import (
        INSTAGRAM_CUTTING_ACCOUNTS,
        INSTAGRAM_CUTTING_HASHTAGS,
        FACEBOOK_CUTTING_GROUPS,
        YOUTUBE_CUTTING_CHANNELS,
        TWITTER_CUTTING_ACCOUNTS,
        WESTERN_NEWS_SOURCES,
        RODEO_VENUES,
        TOP_CUTTING_SIRES,
        SCRAPING_TARGETS_SUMMARY,
        get_all_instagram_accounts,
        get_all_hashtags
    )

    return {
        "success": True,
        "summary": SCRAPING_TARGETS_SUMMARY,
        "instagram": {
            "accounts": INSTAGRAM_CUTTING_ACCOUNTS,
            "hashtags": get_all_hashtags(),
            "total_accounts": len(get_all_instagram_accounts())
        },
        "facebook": {
            "groups": FACEBOOK_CUTTING_GROUPS
        },
        "youtube": {
            "channels": YOUTUBE_CUTTING_CHANNELS
        },
        "twitter": {
            "accounts": TWITTER_CUTTING_ACCOUNTS
        },
        "news_sources": WESTERN_NEWS_SOURCES,
        "venues": RODEO_VENUES,
        "tracked_sires": TOP_CUTTING_SIRES
    }


# --- Comprehensive Western Targets ---

@router.get("/targets/all", summary="Get all western scraping targets")
async def get_all_targets() -> Dict[str, Any]:
    """Get comprehensive list of all western industry scraping targets."""
    from services.scrapers.western_targets import (
        RETAIL_CHAINS, APPAREL_BRANDS, BOOT_BRANDS, HAT_BRANDS,
        SADDLE_BRANDS, TACK_RETAILERS, EQUIPMENT_BRANDS, MARKETPLACES,
        LIFESTYLE_BRANDS, FEED_BRANDS, VET_PRODUCTS, HOME_DECOR,
        TRUCK_ACCESSORIES, COMPETITION_ORGS, HORSE_SALES,
        PEDIGREE_SOURCES, STALLION_DIRECTORIES, NEWS_SOURCES,
        INSTAGRAM_TARGETS, TIKTOK_TARGETS, YOUTUBE_TARGETS,
        FACEBOOK_TARGETS, REDDIT_TARGETS, FORUMS, MAJOR_VENUES,
        get_target_summary
    )

    return {
        "success": True,
        "summary": get_target_summary(),
        "ecommerce": {
            "retail_chains": RETAIL_CHAINS,
            "apparel_brands": APPAREL_BRANDS,
            "boot_brands": BOOT_BRANDS,
            "hat_brands": HAT_BRANDS,
            "saddle_brands": SADDLE_BRANDS,
            "tack_retailers": TACK_RETAILERS,
            "equipment_brands": EQUIPMENT_BRANDS,
            "marketplaces": MARKETPLACES
        },
        "lifestyle": {
            "lifestyle_brands": LIFESTYLE_BRANDS,
            "feed_brands": FEED_BRANDS,
            "vet_products": VET_PRODUCTS,
            "home_decor": HOME_DECOR,
            "truck_accessories": TRUCK_ACCESSORIES
        },
        "competition": {
            "organizations": COMPETITION_ORGS,
            "horse_sales": HORSE_SALES,
            "pedigree_sources": PEDIGREE_SOURCES,
            "stallion_directories": STALLION_DIRECTORIES
        },
        "media": {
            "news_sources": NEWS_SOURCES,
            "forums": FORUMS,
            "venues": MAJOR_VENUES
        },
        "social": {
            "instagram": INSTAGRAM_TARGETS,
            "tiktok": TIKTOK_TARGETS,
            "youtube": YOUTUBE_TARGETS,
            "facebook": FACEBOOK_TARGETS,
            "reddit": REDDIT_TARGETS
        }
    }


@router.get("/targets/retail", summary="Get retail targets")
async def get_retail_targets() -> Dict[str, Any]:
    """Get all retail/e-commerce scraping targets."""
    from services.scrapers.western_targets import (
        RETAIL_CHAINS, APPAREL_BRANDS, BOOT_BRANDS, HAT_BRANDS,
        SADDLE_BRANDS, TACK_RETAILERS, EQUIPMENT_BRANDS, MARKETPLACES
    )

    return {
        "success": True,
        "retail_chains": RETAIL_CHAINS,
        "apparel_brands": APPAREL_BRANDS,
        "boot_brands": BOOT_BRANDS,
        "hat_brands": HAT_BRANDS,
        "saddle_brands": SADDLE_BRANDS,
        "tack_retailers": TACK_RETAILERS,
        "equipment_brands": EQUIPMENT_BRANDS,
        "marketplaces": MARKETPLACES,
        "total_sources": (
            len(RETAIL_CHAINS) + len(APPAREL_BRANDS) + len(BOOT_BRANDS) +
            len(HAT_BRANDS) + len(SADDLE_BRANDS) + len(TACK_RETAILERS) +
            len(EQUIPMENT_BRANDS) + len(MARKETPLACES)
        )
    }


@router.get("/targets/social", summary="Get social media targets")
async def get_social_media_targets() -> Dict[str, Any]:
    """Get all social media scraping targets."""
    from services.scrapers.western_targets import (
        INSTAGRAM_TARGETS, TIKTOK_TARGETS, YOUTUBE_TARGETS,
        FACEBOOK_TARGETS, REDDIT_TARGETS
    )

    return {
        "success": True,
        "instagram": INSTAGRAM_TARGETS,
        "tiktok": TIKTOK_TARGETS,
        "youtube": YOUTUBE_TARGETS,
        "facebook": FACEBOOK_TARGETS,
        "reddit": REDDIT_TARGETS
    }


@router.get("/targets/competition", summary="Get competition data targets")
async def get_competition_targets() -> Dict[str, Any]:
    """Get all competition/horse data scraping targets."""
    from services.scrapers.western_targets import (
        COMPETITION_ORGS, HORSE_SALES, PEDIGREE_SOURCES, STALLION_DIRECTORIES
    )

    return {
        "success": True,
        "organizations": COMPETITION_ORGS,
        "horse_sales": HORSE_SALES,
        "pedigree_sources": PEDIGREE_SOURCES,
        "stallion_directories": STALLION_DIRECTORIES
    }


# --- Health Check ---

@router.get("/health", summary="Data scraping health")
async def data_health() -> Dict[str, Any]:
    """Check data scraping service status."""
    from services.scrapers.western_targets import get_target_summary

    return {
        "status": "ok",
        "target_summary": get_target_summary(),
        "capabilities": [
            "ecommerce_scraping",
            "competition_results",
            "competition_standings",
            "horse_sales",
            "pedigree_lookup",
            "listing_search",
            "social_targets",
            "comprehensive_targets"
        ],
        "ecommerce_sources": ["boot_barn", "cavenders", "ariat", "wrangler", "state_line_tack"],
        "competition_sources": ["ncha", "nrcha", "nrha", "aqha"]
    }
