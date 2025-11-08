# Price Scraping & Intelligence System

## Overview

Infrastructure for scraping prices from hundreds of stores every 12 hours, tracking inventory, detecting sales, and providing real-time price comparisons.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│              Celery Beat Scheduler                      │
│          (Every 12 hours + priority triggers)           │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│            Celery Workers (Distributed)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Scraper Task │  │ Scraper Task │  │ Scraper Task │ │
│  │  (Store 1)   │  │  (Store 2)   │  │  (Store 3)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ...100+ workers...                              │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│         Scraping Methods (Anti-Detection)               │
│  - Rotating Proxies (Bright Data, Smartproxy)          │
│  - Browser Automation (Selenium + Stealth)             │
│  - API Scraping (where available)                      │
│  - Request Headers Rotation                            │
│  - Rate Limiting Per Store                             │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│            Data Processing Pipeline                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Price Parse  │→ │ Deduplication│→ │ Validation   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│        PostgreSQL + Redis Caching                       │
│  ┌─────────────────────────────────────────────┐       │
│  │ ProductPrice table (historical tracking)    │       │
│  │ Redis: Hot cache for current best prices    │       │
│  └─────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────┘
```

## Component 1: Store Scrapers

### Base Scraper Class

```python
# scrapers/base_scraper.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from fake_useragent import UserAgent

class BaseScraper(ABC):
    """Base class for store scrapers."""

    def __init__(self, store_name: str, base_url: str, use_proxy: bool = True):
        self.store_name = store_name
        self.base_url = base_url
        self.use_proxy = use_proxy

        # User agent rotation
        self.ua = UserAgent()

        # Proxy configuration (use rotating proxy service)
        self.proxy = self._get_proxy() if use_proxy else None

        # Rate limiting
        self.request_delay = (2, 5)  # Random delay between requests (seconds)

    def _get_proxy(self) -> Optional[str]:
        """
        Get rotating proxy from service.

        Services like:
        - Bright Data (formerly Luminati)
        - Smartproxy
        - Oxylabs
        """
        # Example: Bright Data rotating proxy
        proxy_host = os.getenv("PROXY_HOST", "brd.superproxy.io")
        proxy_port = os.getenv("PROXY_PORT", "22225")
        proxy_user = os.getenv("PROXY_USER")
        proxy_pass = os.getenv("PROXY_PASS")

        if proxy_user and proxy_pass:
            return f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"

        return None

    def _get_headers(self) -> Dict[str, str]:
        """Generate randomized headers."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def _rate_limit(self):
        """Apply random delay between requests."""
        delay = random.uniform(*self.request_delay)
        time.sleep(delay)

    def get_selenium_driver(self) -> webdriver.Chrome:
        """
        Create Selenium driver with stealth mode.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.ua.random}")

        # Add stealth settings
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')

        driver = webdriver.Chrome(options=chrome_options)

        # Apply stealth JavaScript
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

        return driver

    @abstractmethod
    def scrape_product(self, product_id: str, product_url: str) -> Optional[Dict]:
        """
        Scrape a single product.

        Returns:
            {
                "price": 189.99,
                "original_price": 249.99,  # If on sale
                "is_on_sale": True,
                "in_stock": True,
                "stock_level": "high",
                "shipping_info": {...},
                "sale_end_date": "2024-12-31",
            }
        """
        pass

    @abstractmethod
    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search for products on store.

        Returns list of products with URLs for later scraping.
        """
        pass


class BootBarnScraper(BaseScraper):
    """Scraper for Boot Barn."""

    def __init__(self):
        super().__init__(
            store_name="Boot Barn",
            base_url="https://www.bootbarn.com",
            use_proxy=True
        )

    def scrape_product(self, product_id: str, product_url: str) -> Optional[Dict]:
        """Scrape Boot Barn product page."""
        try:
            self._rate_limit()

            response = requests.get(
                product_url,
                headers=self._get_headers(),
                proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                timeout=15
            )

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse price (adapt selectors to actual site)
            price_elem = soup.select_one('.product-price .price')
            price = float(price_elem.text.strip().replace('$', '').replace(',', '')) if price_elem else None

            # Check for sale
            original_price_elem = soup.select_one('.product-price .original-price')
            original_price = float(original_price_elem.text.strip().replace('$', '').replace(',', '')) if original_price_elem else None

            # Stock status
            stock_elem = soup.select_one('.availability')
            in_stock = "in stock" in stock_elem.text.lower() if stock_elem else False

            # Shipping info
            shipping_elem = soup.select_one('.shipping-info')
            shipping_info = {
                "free_shipping": "free shipping" in shipping_elem.text.lower() if shipping_elem else False
            }

            return {
                "price": price,
                "original_price": original_price,
                "is_on_sale": original_price is not None and original_price > price,
                "in_stock": in_stock,
                "stock_level": "available" if in_stock else "out_of_stock",
                "shipping_info": shipping_info,
                "scraped_at": datetime.utcnow()
            }

        except Exception as e:
            print(f"Error scraping Boot Barn product {product_id}: {e}")
            return None

    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search Boot Barn for products."""
        try:
            search_url = f"{self.base_url}/search?q={query.replace(' ', '+')}"

            self._rate_limit()

            response = requests.get(
                search_url,
                headers=self._get_headers(),
                proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                timeout=15
            )

            soup = BeautifulSoup(response.content, 'html.parser')

            products = []
            product_tiles = soup.select('.product-tile')

            for tile in product_tiles:
                title_elem = tile.select_one('.product-title')
                link_elem = tile.select_one('a.product-link')
                price_elem = tile.select_one('.price')

                if title_elem and link_elem:
                    products.append({
                        "title": title_elem.text.strip(),
                        "url": self.base_url + link_elem['href'],
                        "price": float(price_elem.text.strip().replace('$', '').replace(',', '')) if price_elem else None
                    })

            return products

        except Exception as e:
            print(f"Error searching Boot Barn: {e}")
            return []


class SheplersScraper(BaseScraper):
    """Scraper for Sheplers."""

    def __init__(self):
        super().__init__(
            store_name="Sheplers",
            base_url="https://www.sheplers.com",
            use_proxy=True
        )

    def scrape_product(self, product_id: str, product_url: str) -> Optional[Dict]:
        """Scrape Sheplers product page using Selenium (if JS-heavy)."""
        driver = None
        try:
            driver = self.get_selenium_driver()

            self._rate_limit()

            driver.get(product_url)

            # Wait for price to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-price"))
            )

            # Parse page
            price_elem = driver.find_element(By.CSS_SELECTOR, ".product-price")
            price = float(price_elem.text.strip().replace('$', '').replace(',', ''))

            # Check stock
            try:
                stock_elem = driver.find_element(By.CSS_SELECTOR, ".stock-status")
                in_stock = "in stock" in stock_elem.text.lower()
            except:
                in_stock = True  # Assume in stock if no element

            return {
                "price": price,
                "original_price": None,
                "is_on_sale": False,
                "in_stock": in_stock,
                "stock_level": "available" if in_stock else "out_of_stock",
                "shipping_info": {},
                "scraped_at": datetime.utcnow()
            }

        except Exception as e:
            print(f"Error scraping Sheplers product {product_id}: {e}")
            return None

        finally:
            if driver:
                driver.quit()

    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search Sheplers."""
        # Similar to BootBarn, adapt to Sheplers HTML structure
        pass


# Add scrapers for more stores:
# - Ariat.com
# - Amazon (Western category)
# - Cavender's
# - Murdoch's
# - Tractor Supply Co
# - SmartPak (equestrian)
# - Dover Saddlery (equestrian)
# - State Line Tack
# etc.
```

## Component 2: Celery Task Queue

### Celery Configuration

```python
# celery_app.py

from celery import Celery
from celery.schedules import crontab
import os

# Initialize Celery
celery_app = Celery(
    "rodeoai_scraper",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Rate limiting
    task_rate_limit="10/s",  # Max 10 tasks per second

    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Worker configuration
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Scrape all stores every 12 hours
    "scrape-all-stores": {
        "task": "tasks.scrape_all_stores",
        "schedule": crontab(hour="*/12"),  # Every 12 hours
    },

    # Scrape priority products more frequently
    "scrape-priority-products": {
        "task": "tasks.scrape_priority_products",
        "schedule": crontab(hour="*/4"),  # Every 4 hours
    },

    # Clean up old price data
    "cleanup-old-prices": {
        "task": "tasks.cleanup_old_prices",
        "schedule": crontab(hour="2", minute="0"),  # 2 AM daily
    },

    # Update product best prices cache
    "update-best-prices-cache": {
        "task": "tasks.update_best_prices_cache",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
}
```

### Celery Tasks

```python
# tasks.py

from celery_app import celery_app
from database import get_db
from models import ProductCatalog, ProductPrice
from scrapers import BootBarnScraper, SheplersScraper  # etc.
from datetime import datetime, timedelta
import redis

# Redis for caching
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# Initialize all scrapers
SCRAPERS = {
    "Boot Barn": BootBarnScraper(),
    "Sheplers": SheplersScraper(),
    # Add all other stores...
}


@celery_app.task(bind=True, max_retries=3)
def scrape_product_price(self, product_id: int, store_name: str, product_url: str):
    """
    Scrape price for a single product from a specific store.
    """
    try:
        scraper = SCRAPERS.get(store_name)
        if not scraper:
            return {"error": f"No scraper for store: {store_name}"}

        # Scrape the product
        result = scraper.scrape_product(str(product_id), product_url)

        if not result:
            return {"error": "Scraping failed"}

        # Save to database
        db = next(get_db())

        # Check if price exists
        existing_price = db.query(ProductPrice).filter(
            ProductPrice.product_id == product_id,
            ProductPrice.store_name == store_name
        ).first()

        if existing_price:
            # Update existing
            existing_price.price = result["price"]
            existing_price.original_price = result.get("original_price")
            existing_price.is_on_sale = result.get("is_on_sale", False)
            existing_price.in_stock = result.get("in_stock", True)
            existing_price.stock_level = result.get("stock_level")
            existing_price.shipping_info = result.get("shipping_info")
            existing_price.scraped_at = datetime.utcnow()
            existing_price.last_verified = datetime.utcnow()
        else:
            # Create new
            new_price = ProductPrice(
                product_id=product_id,
                store_name=store_name,
                product_url=product_url,
                price=result["price"],
                original_price=result.get("original_price"),
                is_on_sale=result.get("is_on_sale", False),
                in_stock=result.get("in_stock", True),
                stock_level=result.get("stock_level"),
                shipping_info=result.get("shipping_info"),
            )
            db.add(new_price)

        db.commit()

        return {
            "success": True,
            "product_id": product_id,
            "store": store_name,
            "price": result["price"]
        }

    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task
def scrape_all_stores():
    """
    Main task: Scrape all products from all stores.

    This spawns individual tasks for each product/store combination.
    """
    db = next(get_db())

    # Get all products
    products = db.query(ProductCatalog).all()

    tasks_queued = 0

    for product in products:
        # For each store, create a scraping task
        for store_name in SCRAPERS.keys():
            # Construct product URL for this store
            # (You'd have a mapping of product UPC -> store URLs)
            product_url = get_store_url(product.upc, store_name)

            if product_url:
                # Queue the task
                scrape_product_price.delay(product.id, store_name, product_url)
                tasks_queued += 1

    return {"tasks_queued": tasks_queued}


@celery_app.task
def scrape_priority_products():
    """
    Scrape high-priority products more frequently.

    Priority based on:
    - Popular products
    - Products frequently searched
    - Products with recent price changes
    """
    db = next(get_db())

    # Get priority products (most searched, recently viewed, etc.)
    priority_products = db.query(ProductCatalog).filter(
        ProductCatalog.priority_level == "high"  # Add this field
    ).limit(1000).all()

    for product in priority_products:
        for store_name in SCRAPERS.keys():
            product_url = get_store_url(product.upc, store_name)
            if product_url:
                scrape_product_price.delay(product.id, store_name, product_url)


@celery_app.task
def update_best_prices_cache():
    """
    Update Redis cache with current best prices for fast lookup.
    """
    db = next(get_db())

    products = db.query(ProductCatalog).all()

    for product in products:
        # Get all current prices for this product
        prices = db.query(ProductPrice).filter(
            ProductPrice.product_id == product.id,
            ProductPrice.in_stock == True,
            ProductPrice.scraped_at > datetime.utcnow() - timedelta(hours=24)
        ).order_by(ProductPrice.price.asc()).all()

        if prices:
            best_price = prices[0].price

            # Update product record
            product.current_best_price = best_price

            # Cache in Redis for ultra-fast lookup
            redis_client.setex(
                f"best_price:{product.id}",
                3600,  # 1 hour TTL
                str(best_price)
            )

    db.commit()


@celery_app.task
def cleanup_old_prices():
    """Delete price records older than 90 days."""
    db = next(get_db())

    cutoff_date = datetime.utcnow() - timedelta(days=90)

    deleted = db.query(ProductPrice).filter(
        ProductPrice.scraped_at < cutoff_date
    ).delete()

    db.commit()

    return {"deleted_records": deleted}


def get_store_url(upc: str, store_name: str) -> Optional[str]:
    """
    Map product UPC to store-specific URL.

    This would be populated by:
    1. Initial product discovery scraping
    2. Manual mapping for common products
    3. Search API if store provides one
    """
    # Query a mapping table or cache
    pass
```

## Component 3: Price Intelligence Service

```python
# price_intelligence.py

from typing import List, Dict, Optional
from database import get_db
from models import ProductPrice, ProductCatalog
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

class PriceIntelligenceService:
    """Service for intelligent price queries and analytics."""

    @staticmethod
    def get_product_prices(
        product_id: int,
        limit: int = 10,
        include_out_of_stock: bool = False
    ) -> Dict:
        """
        Get current prices for a product across all stores.

        Returns:
            {
                "product_id": 12345,
                "product_name": "Ariat Heritage Roughstock",
                "lowest_price": 189.99,
                "average_price": 215.50,
                "prices": [
                    {
                        "store": "Boot Barn",
                        "price": 189.99,
                        "original_price": 249.99,
                        "is_on_sale": true,
                        "in_stock": true,
                        "url": "...",
                        "last_updated": "2024-01-15T10:30:00Z"
                    },
                    ...
                ],
                "price_history": {...}
            }
        """
        db = next(get_db())

        # Get product info
        product = db.query(ProductCatalog).filter(
            ProductCatalog.id == product_id
        ).first()

        if not product:
            return {"error": "Product not found"}

        # Get current prices
        query = db.query(ProductPrice).filter(
            ProductPrice.product_id == product_id,
            ProductPrice.scraped_at > datetime.utcnow() - timedelta(hours=24)
        )

        if not include_out_of_stock:
            query = query.filter(ProductPrice.in_stock == True)

        prices = query.order_by(ProductPrice.price.asc()).limit(limit).all()

        price_list = []
        for p in prices:
            price_list.append({
                "store": p.store_name,
                "price": p.price,
                "original_price": p.original_price,
                "is_on_sale": p.is_on_sale,
                "in_stock": p.in_stock,
                "stock_level": p.stock_level,
                "url": p.product_url,
                "shipping_info": p.shipping_info,
                "last_updated": p.scraped_at.isoformat()
            })

        # Calculate statistics
        prices_values = [p.price for p in prices if p.in_stock]
        lowest_price = min(prices_values) if prices_values else None
        average_price = sum(prices_values) / len(prices_values) if prices_values else None

        return {
            "product_id": product_id,
            "product_name": f"{product.brand} {product.model}",
            "category": product.category,
            "lowest_price": lowest_price,
            "average_price": round(average_price, 2) if average_price else None,
            "msrp": product.msrp,
            "prices": price_list,
            "total_stores": len(price_list),
            "stores_in_stock": len([p for p in price_list if p["in_stock"]])
        }

    @staticmethod
    def get_price_history(product_id: int, days: int = 30) -> List[Dict]:
        """Get price history for trend analysis."""
        db = next(get_db())

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = db.query(ProductPrice).filter(
            ProductPrice.product_id == product_id,
            ProductPrice.scraped_at > cutoff_date
        ).order_by(ProductPrice.scraped_at.asc()).all()

        history = []
        for p in prices:
            history.append({
                "date": p.scraped_at.isoformat(),
                "store": p.store_name,
                "price": p.price,
                "in_stock": p.in_stock
            })

        return history

    @staticmethod
    def detect_sales(days_lookback: int = 7) -> List[Dict]:
        """
        Detect products currently on sale.
        """
        db = next(get_db())

        cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)

        sales = db.query(ProductPrice).filter(
            ProductPrice.is_on_sale == True,
            ProductPrice.in_stock == True,
            ProductPrice.scraped_at > cutoff_date
        ).all()

        sale_list = []
        for sale in sales:
            product = db.query(ProductCatalog).filter(
                ProductCatalog.id == sale.product_id
            ).first()

            if product:
                discount_percent = (
                    (sale.original_price - sale.price) / sale.original_price * 100
                ) if sale.original_price else 0

                sale_list.append({
                    "product_id": product.id,
                    "product_name": f"{product.brand} {product.model}",
                    "store": sale.store_name,
                    "sale_price": sale.price,
                    "original_price": sale.original_price,
                    "discount_percent": round(discount_percent, 1),
                    "url": sale.product_url
                })

        return sale_list
```

Let me continue with legal considerations and the full implementation roadmap in the next file...
