"""
RodeoAI Backend Configuration
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import List, Optional
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Server
        self.port: int = int(os.getenv("PORT", "8000"))
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug: bool = self.environment == "development"

        # CORS
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins: List[str] = (
            ["*"] if cors_origins == "*"
            else [origin.strip() for origin in cors_origins.split(",")]
        )

        # API Keys
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.api_key: Optional[str] = os.getenv("API_KEY")  # For securing endpoints

        # Rate Limiting
        self.rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_period: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

        # Scraping
        self.scrape_timeout: int = int(os.getenv("SCRAPE_TIMEOUT", "30"))
        self.scrape_headless: bool = os.getenv("SCRAPE_HEADLESS", "true").lower() == "true"
        self.scrape_max_concurrent: int = int(os.getenv("SCRAPE_MAX_CONCURRENT", "5"))
        self.scrape_user_agent: str = os.getenv(
            "SCRAPE_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Browser
        self.browser_type: str = os.getenv("BROWSER_TYPE", "chromium")
        self.browser_executable_path: Optional[str] = os.getenv("BROWSER_EXECUTABLE_PATH")

        # Caching
        self.cache_enabled: bool = os.getenv("CACHE_ENABLED", "false").lower() == "true"
        self.redis_url: Optional[str] = os.getenv("REDIS_URL")
        self.cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))

        # Proxy
        self.proxy_url: Optional[str] = os.getenv("PROXY_URL")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
