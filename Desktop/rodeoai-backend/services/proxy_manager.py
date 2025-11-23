"""
Proxy Manager with Rotation
Handles proxy rotation, health checks, and rate limit bypass.
"""

import asyncio
import random
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
import logging

logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    """Represents a proxy server."""
    url: str
    protocol: str = "http"  # http, https, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None

    # Health tracking
    is_healthy: bool = True
    last_used: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    fail_count: int = 0
    success_count: int = 0
    avg_response_time: float = 0

    # Rate limiting
    requests_this_minute: int = 0
    minute_started: Optional[datetime] = None
    max_requests_per_minute: int = 30

    @property
    def full_url(self) -> str:
        if self.username and self.password:
            protocol = self.url.split("://")[0] if "://" in self.url else self.protocol
            host = self.url.split("://")[-1]
            return f"{protocol}://{self.username}:{self.password}@{host}"
        return self.url

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        if total == 0:
            return 1.0
        return self.success_count / total

    def can_use(self) -> bool:
        """Check if proxy can be used (healthy and within rate limits)."""
        if not self.is_healthy:
            return False

        # Check rate limit
        now = datetime.utcnow()
        if self.minute_started:
            if now - self.minute_started > timedelta(minutes=1):
                self.requests_this_minute = 0
                self.minute_started = now
            elif self.requests_this_minute >= self.max_requests_per_minute:
                return False

        return True

    def mark_used(self):
        """Mark proxy as used."""
        now = datetime.utcnow()
        self.last_used = now

        if not self.minute_started or now - self.minute_started > timedelta(minutes=1):
            self.minute_started = now
            self.requests_this_minute = 1
        else:
            self.requests_this_minute += 1

    def mark_success(self, response_time: float):
        """Mark a successful request."""
        self.success_count += 1
        self.fail_count = max(0, self.fail_count - 1)  # Reduce fail count on success

        # Update average response time
        total = self.success_count
        self.avg_response_time = ((self.avg_response_time * (total - 1)) + response_time) / total

    def mark_failure(self):
        """Mark a failed request."""
        self.fail_count += 1

        # Disable if too many failures
        if self.fail_count >= 5:
            self.is_healthy = False
            logger.warning(f"Proxy {self.url} marked unhealthy after {self.fail_count} failures")


class ProxyManager:
    """
    Manages a pool of proxies with intelligent rotation.
    """

    def __init__(
        self,
        proxies: List[str] = None,
        rotation_strategy: str = "round_robin",  # round_robin, random, least_used, fastest
        health_check_interval: int = 300,  # seconds
        test_url: str = "https://httpbin.org/ip"
    ):
        self._proxies: List[Proxy] = []
        self.rotation_strategy = rotation_strategy
        self.health_check_interval = health_check_interval
        self.test_url = test_url
        self._current_index = 0
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None

        if proxies:
            for p in proxies:
                self.add_proxy(p)

    def add_proxy(self, proxy_url: str, **kwargs):
        """Add a proxy to the pool."""
        proxy = Proxy(url=proxy_url, **kwargs)
        self._proxies.append(proxy)
        logger.info(f"Added proxy: {proxy_url}")

    def add_proxies_from_list(self, proxy_list: List[str]):
        """Add multiple proxies from a list."""
        for p in proxy_list:
            self.add_proxy(p)

    def add_proxies_from_file(self, filepath: str):
        """Load proxies from a file (one per line)."""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.add_proxy(line)
            logger.info(f"Loaded {len(self._proxies)} proxies from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load proxies from {filepath}: {e}")

    async def get_proxy(self) -> Optional[Proxy]:
        """Get the next proxy based on rotation strategy."""
        async with self._lock:
            available = [p for p in self._proxies if p.can_use()]

            if not available:
                logger.warning("No available proxies")
                return None

            proxy = None

            if self.rotation_strategy == "round_robin":
                self._current_index = self._current_index % len(available)
                proxy = available[self._current_index]
                self._current_index += 1

            elif self.rotation_strategy == "random":
                proxy = random.choice(available)

            elif self.rotation_strategy == "least_used":
                proxy = min(available, key=lambda p: p.requests_this_minute)

            elif self.rotation_strategy == "fastest":
                proxy = min(available, key=lambda p: p.avg_response_time if p.avg_response_time > 0 else float('inf'))

            elif self.rotation_strategy == "best":
                # Combines success rate and speed
                proxy = max(available, key=lambda p: p.success_rate / (p.avg_response_time + 0.1))

            if proxy:
                proxy.mark_used()

            return proxy

    async def mark_proxy_result(self, proxy: Proxy, success: bool, response_time: float = 0):
        """Mark the result of using a proxy."""
        async with self._lock:
            if success:
                proxy.mark_success(response_time)
            else:
                proxy.mark_failure()

    async def health_check(self, proxy: Proxy) -> bool:
        """Check if a proxy is healthy."""
        try:
            start = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.test_url,
                    proxy=proxy.full_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        elapsed = time.time() - start
                        proxy.is_healthy = True
                        proxy.last_checked = datetime.utcnow()
                        proxy.avg_response_time = elapsed
                        return True
        except Exception as e:
            logger.debug(f"Proxy health check failed for {proxy.url}: {e}")

        proxy.is_healthy = False
        proxy.last_checked = datetime.utcnow()
        return False

    async def health_check_all(self):
        """Run health checks on all proxies."""
        logger.info(f"Running health check on {len(self._proxies)} proxies")

        tasks = [self.health_check(p) for p in self._proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        healthy = sum(1 for r in results if r is True)
        logger.info(f"Health check complete: {healthy}/{len(self._proxies)} healthy")

    async def start_health_checks(self):
        """Start periodic health checks."""
        async def _check_loop():
            while True:
                await asyncio.sleep(self.health_check_interval)
                await self.health_check_all()

        self._health_check_task = asyncio.create_task(_check_loop())

    async def stop_health_checks(self):
        """Stop periodic health checks."""
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        total = len(self._proxies)
        healthy = sum(1 for p in self._proxies if p.is_healthy)
        available = sum(1 for p in self._proxies if p.can_use())

        return {
            "total_proxies": total,
            "healthy": healthy,
            "available": available,
            "rotation_strategy": self.rotation_strategy,
            "proxies": [
                {
                    "url": p.url,
                    "healthy": p.is_healthy,
                    "success_rate": round(p.success_rate * 100, 1),
                    "avg_response_time": round(p.avg_response_time, 3),
                    "requests_this_minute": p.requests_this_minute
                }
                for p in self._proxies
            ]
        }

    @property
    def has_proxies(self) -> bool:
        return len(self._proxies) > 0

    @property
    def healthy_count(self) -> int:
        return sum(1 for p in self._proxies if p.is_healthy)


class RateLimitHandler:
    """
    Handles rate limiting with exponential backoff and retry logic.
    """

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

        # Track rate limits per domain
        self._domain_limits: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        # Add jitter (±20%)
        jitter = delay * 0.2 * (random.random() * 2 - 1)
        return delay + jitter

    async def wait_if_needed(self, domain: str):
        """Wait if we're rate limited for a domain."""
        async with self._lock:
            if domain in self._domain_limits:
                wait_until = self._domain_limits[domain]
                now = datetime.utcnow()

                if now < wait_until:
                    delay = (wait_until - now).total_seconds()
                    logger.info(f"Rate limited for {domain}, waiting {delay:.1f}s")
                    await asyncio.sleep(delay)

    async def mark_rate_limited(self, domain: str, retry_after: int = None):
        """Mark a domain as rate limited."""
        async with self._lock:
            delay = retry_after if retry_after else 60
            self._domain_limits[domain] = datetime.utcnow() + timedelta(seconds=delay)
            logger.warning(f"Rate limited for {domain}, will retry after {delay}s")

    async def execute_with_retry(
        self,
        func,
        *args,
        domain: str = None,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Wait if rate limited
                if domain:
                    await self.wait_if_needed(domain)

                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check for rate limit indicators
                is_rate_limit = any(x in error_str for x in [
                    "rate limit", "too many requests", "429",
                    "throttl", "slow down", "try again later"
                ])

                if is_rate_limit and domain:
                    await self.mark_rate_limited(domain)

                if attempt < self.max_retries - 1:
                    delay = self.calculate_delay(attempt)
                    logger.info(f"Retry {attempt + 1}/{self.max_retries} after {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} retries failed: {e}")

        raise last_error


# Global instances
_proxy_manager: Optional[ProxyManager] = None
_rate_limiter: Optional[RateLimitHandler] = None


def get_proxy_manager() -> ProxyManager:
    """Get or create global proxy manager."""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager(rotation_strategy="best")
    return _proxy_manager


def get_rate_limiter() -> RateLimitHandler:
    """Get or create global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimitHandler()
    return _rate_limiter
