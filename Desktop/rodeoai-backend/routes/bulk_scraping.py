"""
Bulk Scraping API Routes
High-volume scraping endpoints with job queue, export, and monitoring.
"""

import csv
import json
import io
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from services.bulk_engine import (
    get_engine, JobPriority, JobStatus,
    BulkScrapingEngine
)
from services.proxy_manager import get_proxy_manager, get_rate_limiter

router = APIRouter(prefix="/api/bulk", tags=["bulk-scraping"])


# --- Request Models ---

class BulkProfilesRequest(BaseModel):
    """Request for bulk profile scraping."""
    platform: str = Field(..., description="Platform to scrape")
    usernames: List[str] = Field(..., description="List of usernames to scrape")
    priority: int = Field(default=5, ge=1, le=20, description="Job priority (1-20)")


class BulkPostsRequest(BaseModel):
    """Request for bulk posts scraping."""
    platform: str = Field(..., description="Platform to scrape")
    usernames: List[str] = Field(..., description="List of usernames")
    limit_per_user: int = Field(default=100, ge=1, le=1000, description="Posts per user")
    priority: int = Field(default=5)


class BulkSearchRequest(BaseModel):
    """Request for bulk search across queries."""
    platform: str = Field(..., description="Platform to search")
    queries: List[str] = Field(..., description="List of search queries")
    limit_per_query: int = Field(default=100, ge=1, le=1000)
    priority: int = Field(default=5)


class MassScrapRequest(BaseModel):
    """Request for massive scraping operation."""
    platform: str
    job_type: str = Field(..., description="profile, posts, or search")
    targets: List[str] = Field(..., description="Usernames or queries")
    limit: int = Field(default=100, description="Results per target")
    include_posts: bool = Field(default=False, description="Also scrape posts for profiles")
    posts_limit: int = Field(default=50, description="Posts per user if include_posts")


class ProxyConfig(BaseModel):
    """Proxy configuration."""
    proxies: List[str] = Field(..., description="List of proxy URLs")
    rotation_strategy: str = Field(default="best", description="round_robin, random, least_used, fastest, best")


# --- Job Management Endpoints ---

@router.post("/profiles", summary="Bulk scrape profiles")
async def bulk_scrape_profiles(request: BulkProfilesRequest) -> Dict[str, Any]:
    """
    Submit a bulk job to scrape multiple profiles.
    Returns a job ID to track progress.
    """
    if len(request.usernames) > 1000:
        raise HTTPException(400, "Maximum 1000 usernames per request")

    engine = await get_engine()

    job_id = await engine.submit_bulk_job(
        name=f"bulk_profiles_{request.platform}",
        job_type="profile",
        platform=request.platform,
        targets=request.usernames,
        priority=JobPriority(request.priority)
    )

    return {
        "job_id": job_id,
        "total_targets": len(request.usernames),
        "status": "submitted",
        "message": f"Bulk scraping {len(request.usernames)} profiles"
    }


@router.post("/posts", summary="Bulk scrape posts from multiple users")
async def bulk_scrape_posts(request: BulkPostsRequest) -> Dict[str, Any]:
    """
    Submit a bulk job to scrape posts from multiple users.
    """
    if len(request.usernames) > 500:
        raise HTTPException(400, "Maximum 500 usernames per request")

    engine = await get_engine()

    job_id = await engine.submit_bulk_job(
        name=f"bulk_posts_{request.platform}",
        job_type="posts",
        platform=request.platform,
        targets=request.usernames,
        params={"limit": request.limit_per_user},
        priority=JobPriority(request.priority)
    )

    return {
        "job_id": job_id,
        "total_targets": len(request.usernames),
        "posts_per_user": request.limit_per_user,
        "estimated_total_posts": len(request.usernames) * request.limit_per_user,
        "status": "submitted"
    }


@router.post("/search", summary="Bulk search across queries")
async def bulk_search(request: BulkSearchRequest) -> Dict[str, Any]:
    """
    Submit bulk search jobs for multiple queries.
    """
    if len(request.queries) > 200:
        raise HTTPException(400, "Maximum 200 queries per request")

    engine = await get_engine()

    job_id = await engine.submit_bulk_job(
        name=f"bulk_search_{request.platform}",
        job_type="search",
        platform=request.platform,
        targets=request.queries,
        params={"limit": request.limit_per_query},
        priority=JobPriority(request.priority)
    )

    return {
        "job_id": job_id,
        "total_queries": len(request.queries),
        "results_per_query": request.limit_per_query,
        "estimated_total_results": len(request.queries) * request.limit_per_query,
        "status": "submitted"
    }


@router.post("/mass-scrape", summary="Massive scraping operation")
async def mass_scrape(request: MassScrapRequest) -> Dict[str, Any]:
    """
    Submit a massive scraping operation.
    Can scrape thousands of targets with optional cascade (profiles + their posts).
    """
    if len(request.targets) > 5000:
        raise HTTPException(400, "Maximum 5000 targets per request")

    engine = await get_engine()

    # Submit main job
    job_id = await engine.submit_bulk_job(
        name=f"mass_{request.job_type}_{request.platform}",
        job_type=request.job_type,
        platform=request.platform,
        targets=request.targets,
        params={"limit": request.limit},
        priority=JobPriority.HIGH
    )

    response = {
        "job_id": job_id,
        "total_targets": len(request.targets),
        "job_type": request.job_type,
        "status": "submitted"
    }

    # If scraping profiles and want posts too, queue those as well
    if request.include_posts and request.job_type == "profile":
        posts_job_id = await engine.submit_bulk_job(
            name=f"mass_posts_{request.platform}",
            job_type="posts",
            platform=request.platform,
            targets=request.targets,
            params={"limit": request.posts_limit},
            priority=JobPriority.NORMAL
        )
        response["posts_job_id"] = posts_job_id
        response["message"] = f"Scraping {len(request.targets)} profiles + their posts"

    return response


# --- Job Status Endpoints ---

@router.get("/job/{job_id}", summary="Get job status")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a bulk job."""
    engine = await get_engine()

    bulk_job = engine.get_bulk_job(job_id)
    if bulk_job:
        return {
            "type": "bulk",
            **bulk_job.to_dict()
        }

    single_job = engine.get_job(job_id)
    if single_job:
        return {
            "type": "single",
            **single_job.to_dict()
        }

    raise HTTPException(404, f"Job {job_id} not found")


@router.get("/job/{job_id}/results", summary="Get job results")
async def get_job_results(job_id: str) -> Dict[str, Any]:
    """Get results from a completed bulk job."""
    engine = await get_engine()

    bulk_job = engine.get_bulk_job(job_id)
    if not bulk_job:
        raise HTTPException(404, f"Job {job_id} not found")

    results = engine.get_bulk_job_results(job_id)

    return {
        "job_id": job_id,
        "status": bulk_job.status.value,
        "progress": bulk_job.progress,
        "total": bulk_job.total,
        "completed": bulk_job.completed,
        "failed": bulk_job.failed,
        "results": results
    }


# --- Export Endpoints ---

@router.get("/job/{job_id}/export/json", summary="Export results as JSON")
async def export_json(job_id: str) -> StreamingResponse:
    """Export job results as a JSON file."""
    engine = await get_engine()

    bulk_job = engine.get_bulk_job(job_id)
    if not bulk_job:
        raise HTTPException(404, f"Job {job_id} not found")

    results = engine.get_bulk_job_results(job_id)

    output = {
        "job_id": job_id,
        "exported_at": datetime.utcnow().isoformat(),
        "total_results": len(results),
        "data": results
    }

    json_str = json.dumps(output, indent=2, default=str)

    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=scrape_results_{job_id}.json"
        }
    )


@router.get("/job/{job_id}/export/csv", summary="Export results as CSV")
async def export_csv(job_id: str) -> StreamingResponse:
    """Export job results as a CSV file."""
    engine = await get_engine()

    bulk_job = engine.get_bulk_job(job_id)
    if not bulk_job:
        raise HTTPException(404, f"Job {job_id} not found")

    results = engine.get_bulk_job_results(job_id)

    # Flatten results for CSV
    rows = []
    for r in results:
        if r.get("result"):
            result_data = r["result"]
            if isinstance(result_data, dict):
                # Handle posts array
                if "posts" in result_data:
                    for post in result_data["posts"]:
                        rows.append({
                            "target": r["target"],
                            "status": r["status"],
                            **post
                        })
                else:
                    rows.append({
                        "target": r["target"],
                        "status": r["status"],
                        **result_data
                    })
        else:
            rows.append({
                "target": r["target"],
                "status": r["status"],
                "error": r.get("error")
            })

    if not rows:
        rows = [{"message": "No data"}]

    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=scrape_results_{job_id}.csv"
        }
    )


# --- Engine Stats & Management ---

@router.get("/stats", summary="Get scraping engine stats")
async def get_stats() -> Dict[str, Any]:
    """Get scraping engine statistics."""
    engine = await get_engine()
    queue_size = await engine.get_queue_size()

    return {
        **engine.get_stats(),
        "queue_size": queue_size
    }


@router.get("/proxy/stats", summary="Get proxy pool stats")
async def get_proxy_stats() -> Dict[str, Any]:
    """Get proxy pool statistics."""
    proxy_manager = get_proxy_manager()
    return proxy_manager.get_stats()


@router.post("/proxy/configure", summary="Configure proxy pool")
async def configure_proxies(config: ProxyConfig) -> Dict[str, Any]:
    """Add proxies to the rotation pool."""
    proxy_manager = get_proxy_manager()

    for proxy_url in config.proxies:
        proxy_manager.add_proxy(proxy_url)

    proxy_manager.rotation_strategy = config.rotation_strategy

    # Run initial health check
    await proxy_manager.health_check_all()

    return {
        "message": f"Added {len(config.proxies)} proxies",
        "total_proxies": len(proxy_manager._proxies),
        "healthy": proxy_manager.healthy_count,
        "rotation_strategy": config.rotation_strategy
    }


@router.post("/proxy/health-check", summary="Run proxy health check")
async def run_proxy_health_check() -> Dict[str, Any]:
    """Manually trigger proxy health check."""
    proxy_manager = get_proxy_manager()
    await proxy_manager.health_check_all()

    return {
        "message": "Health check complete",
        **proxy_manager.get_stats()
    }


# --- Quick Scrape Endpoints (for smaller batches) ---

@router.post("/quick/profiles/{platform}", summary="Quick batch profile scrape")
async def quick_profiles(
    platform: str,
    usernames: List[str] = None
) -> Dict[str, Any]:
    """
    Synchronously scrape up to 50 profiles and return results immediately.
    For larger batches, use the async bulk endpoints.
    """
    if not usernames or len(usernames) > 50:
        raise HTTPException(400, "Provide 1-50 usernames")

    from services.scrapers import (
        TwitterScraper, InstagramScraper, LinkedInScraper,
        RedditScraper, YouTubeScraper
    )

    scrapers = {
        "twitter": TwitterScraper,
        "instagram": InstagramScraper,
        "linkedin": LinkedInScraper,
        "reddit": RedditScraper,
        "youtube": YouTubeScraper
    }

    if platform not in scrapers:
        raise HTTPException(400, f"Unknown platform: {platform}")

    scraper = scrapers[platform]()
    results = []

    try:
        import asyncio
        tasks = [scraper.scrape_profile(u) for u in usernames]
        profiles = await asyncio.gather(*tasks, return_exceptions=True)

        for username, profile in zip(usernames, profiles):
            if isinstance(profile, Exception):
                results.append({"username": username, "error": str(profile)})
            elif profile:
                results.append({"username": username, "data": profile.to_dict()})
            else:
                results.append({"username": username, "error": "Not found"})

    finally:
        await scraper.close()

    return {
        "platform": platform,
        "total": len(usernames),
        "successful": sum(1 for r in results if "data" in r),
        "results": results
    }
