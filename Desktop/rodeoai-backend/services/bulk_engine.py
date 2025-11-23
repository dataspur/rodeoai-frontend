"""
High-Volume Scraping Engine
Async job queue with worker pools for massive parallel scraping.
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    URGENT = 20


@dataclass
class ScrapeJob:
    """Represents a single scrape job."""
    id: str
    job_type: str  # profile, posts, search, url
    platform: str
    target: str  # username, query, or URL
    params: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "job_type": self.job_type,
            "platform": self.platform,
            "target": self.target,
            "params": self.params,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "retries": self.retries
        }


@dataclass
class BulkJob:
    """Represents a bulk scraping job containing multiple scrape jobs."""
    id: str
    name: str
    jobs: List[ScrapeJob]
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total: int = 0
    completed: int = 0
    failed: int = 0

    def __post_init__(self):
        self.total = len(self.jobs)

    @property
    def progress(self) -> float:
        if self.total == 0:
            return 0
        return (self.completed + self.failed) / self.total * 100

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "progress": self.progress
        }


class ScrapingQueue:
    """Priority queue for scraping jobs."""

    def __init__(self):
        self._queues: Dict[JobPriority, deque] = {
            priority: deque() for priority in JobPriority
        }
        self._lock = asyncio.Lock()

    async def put(self, job: ScrapeJob):
        async with self._lock:
            self._queues[job.priority].append(job)

    async def get(self) -> Optional[ScrapeJob]:
        async with self._lock:
            # Check queues from highest to lowest priority
            for priority in sorted(JobPriority, key=lambda x: x.value, reverse=True):
                if self._queues[priority]:
                    return self._queues[priority].popleft()
        return None

    async def size(self) -> int:
        async with self._lock:
            return sum(len(q) for q in self._queues.values())

    async def clear(self):
        async with self._lock:
            for q in self._queues.values():
                q.clear()


class WorkerPool:
    """Pool of workers for concurrent scraping."""

    def __init__(
        self,
        num_workers: int = 10,
        rate_limit: float = 0.5,  # seconds between requests per worker
    ):
        self.num_workers = num_workers
        self.rate_limit = rate_limit
        self._workers: List[asyncio.Task] = []
        self._running = False
        self._queue: Optional[ScrapingQueue] = None
        self._job_handler: Optional[Callable] = None
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def start(self, queue: ScrapingQueue, job_handler: Callable):
        """Start the worker pool."""
        self._queue = queue
        self._job_handler = job_handler
        self._running = True
        self._semaphore = asyncio.Semaphore(self.num_workers)

        logger.info(f"Starting worker pool with {self.num_workers} workers")

        for i in range(self.num_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)

    async def stop(self):
        """Stop all workers."""
        self._running = False
        for worker in self._workers:
            worker.cancel()
        self._workers.clear()
        logger.info("Worker pool stopped")

    async def _worker(self, worker_id: int):
        """Worker coroutine that processes jobs from the queue."""
        logger.info(f"Worker {worker_id} started")

        while self._running:
            try:
                async with self._semaphore:
                    job = await self._queue.get()

                    if job is None:
                        await asyncio.sleep(0.1)
                        continue

                    logger.info(f"Worker {worker_id} processing job {job.id}")

                    try:
                        job.status = JobStatus.RUNNING
                        job.started_at = datetime.utcnow()

                        result = await self._job_handler(job)

                        job.result = result
                        job.status = JobStatus.COMPLETED
                        job.completed_at = datetime.utcnow()

                    except Exception as e:
                        logger.error(f"Job {job.id} failed: {e}")
                        job.error = str(e)
                        job.retries += 1

                        if job.retries < job.max_retries:
                            logger.info(f"Retrying job {job.id} (attempt {job.retries})")
                            job.status = JobStatus.PENDING
                            await self._queue.put(job)
                        else:
                            job.status = JobStatus.FAILED
                            job.completed_at = datetime.utcnow()

                    # Rate limiting
                    await asyncio.sleep(self.rate_limit)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Worker {worker_id} stopped")


class BulkScrapingEngine:
    """
    High-volume scraping engine with job queue and worker pools.
    Handles massive parallel scraping operations.
    """

    def __init__(
        self,
        max_workers: int = 20,
        rate_limit: float = 0.3,
        max_concurrent_bulk_jobs: int = 5
    ):
        self.queue = ScrapingQueue()
        self.worker_pool = WorkerPool(num_workers=max_workers, rate_limit=rate_limit)
        self.max_concurrent_bulk_jobs = max_concurrent_bulk_jobs

        self._jobs: Dict[str, ScrapeJob] = {}
        self._bulk_jobs: Dict[str, BulkJob] = {}
        self._running = False
        self._scrapers: Dict[str, Any] = {}

    async def start(self):
        """Start the scraping engine."""
        if self._running:
            return

        self._running = True
        await self.worker_pool.start(self.queue, self._process_job)
        logger.info("Bulk scraping engine started")

    async def stop(self):
        """Stop the scraping engine."""
        self._running = False
        await self.worker_pool.stop()

        # Close all scrapers
        for scraper in self._scrapers.values():
            await scraper.close()
        self._scrapers.clear()

        logger.info("Bulk scraping engine stopped")

    def register_scraper(self, platform: str, scraper):
        """Register a scraper for a platform."""
        self._scrapers[platform] = scraper

    async def _process_job(self, job: ScrapeJob) -> Dict:
        """Process a single scrape job."""
        scraper = self._scrapers.get(job.platform)
        if not scraper:
            raise ValueError(f"No scraper registered for platform: {job.platform}")

        if job.job_type == "profile":
            result = await scraper.scrape_profile(job.target)
            return result.to_dict() if result else {"error": "Profile not found"}

        elif job.job_type == "posts":
            limit = job.params.get("limit", 100)
            results = await scraper.scrape_posts(job.target, limit=limit)
            return {"posts": [p.to_dict() for p in results], "count": len(results)}

        elif job.job_type == "search":
            limit = job.params.get("limit", 100)
            results = await scraper.search_posts(job.target, limit=limit)
            return {"results": [p.to_dict() for p in results], "count": len(results)}

        elif job.job_type == "url":
            result = await scraper.scrape_url(job.target)
            return result

        else:
            raise ValueError(f"Unknown job type: {job.job_type}")

    async def submit_job(
        self,
        job_type: str,
        platform: str,
        target: str,
        params: Dict = None,
        priority: JobPriority = JobPriority.NORMAL
    ) -> str:
        """Submit a single scraping job."""
        job = ScrapeJob(
            id=str(uuid.uuid4()),
            job_type=job_type,
            platform=platform,
            target=target,
            params=params or {},
            priority=priority
        )

        self._jobs[job.id] = job
        await self.queue.put(job)

        return job.id

    async def submit_bulk_job(
        self,
        name: str,
        job_type: str,
        platform: str,
        targets: List[str],
        params: Dict = None,
        priority: JobPriority = JobPriority.NORMAL
    ) -> str:
        """Submit a bulk scraping job for multiple targets."""
        jobs = []
        for target in targets:
            job = ScrapeJob(
                id=str(uuid.uuid4()),
                job_type=job_type,
                platform=platform,
                target=target,
                params=params or {},
                priority=priority
            )
            jobs.append(job)
            self._jobs[job.id] = job

        bulk_job = BulkJob(
            id=str(uuid.uuid4()),
            name=name,
            jobs=jobs
        )
        self._bulk_jobs[bulk_job.id] = bulk_job

        # Queue all jobs
        for job in jobs:
            await self.queue.put(job)

        bulk_job.status = JobStatus.RUNNING

        return bulk_job.id

    def get_job(self, job_id: str) -> Optional[ScrapeJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def get_bulk_job(self, bulk_job_id: str) -> Optional[BulkJob]:
        """Get a bulk job by ID."""
        bulk_job = self._bulk_jobs.get(bulk_job_id)
        if bulk_job:
            # Update counts
            bulk_job.completed = sum(1 for j in bulk_job.jobs if j.status == JobStatus.COMPLETED)
            bulk_job.failed = sum(1 for j in bulk_job.jobs if j.status == JobStatus.FAILED)

            if bulk_job.completed + bulk_job.failed >= bulk_job.total:
                bulk_job.status = JobStatus.COMPLETED
                bulk_job.completed_at = datetime.utcnow()

        return bulk_job

    def get_bulk_job_results(self, bulk_job_id: str) -> List[Dict]:
        """Get all results from a bulk job."""
        bulk_job = self._bulk_jobs.get(bulk_job_id)
        if not bulk_job:
            return []

        results = []
        for job in bulk_job.jobs:
            results.append({
                "target": job.target,
                "status": job.status.value,
                "result": job.result,
                "error": job.error
            })

        return results

    async def get_queue_size(self) -> int:
        """Get current queue size."""
        return await self.queue.size()

    def get_stats(self) -> Dict:
        """Get engine statistics."""
        total_jobs = len(self._jobs)
        completed = sum(1 for j in self._jobs.values() if j.status == JobStatus.COMPLETED)
        failed = sum(1 for j in self._jobs.values() if j.status == JobStatus.FAILED)
        running = sum(1 for j in self._jobs.values() if j.status == JobStatus.RUNNING)
        pending = sum(1 for j in self._jobs.values() if j.status == JobStatus.PENDING)

        return {
            "total_jobs": total_jobs,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "bulk_jobs": len(self._bulk_jobs),
            "workers": self.worker_pool.num_workers
        }


# Global engine instance
_engine: Optional[BulkScrapingEngine] = None


async def get_engine() -> BulkScrapingEngine:
    """Get or create the global scraping engine."""
    global _engine
    if _engine is None:
        _engine = BulkScrapingEngine(max_workers=20, rate_limit=0.3)
        await _engine.start()

        # Register scrapers
        from services.scrapers import (
            TwitterScraper, InstagramScraper, LinkedInScraper,
            RedditScraper, YouTubeScraper
        )

        _engine.register_scraper("twitter", TwitterScraper())
        _engine.register_scraper("instagram", InstagramScraper())
        _engine.register_scraper("linkedin", LinkedInScraper())
        _engine.register_scraper("reddit", RedditScraper())
        _engine.register_scraper("youtube", YouTubeScraper())

    return _engine


async def shutdown_engine():
    """Shutdown the global engine."""
    global _engine
    if _engine:
        await _engine.stop()
        _engine = None
