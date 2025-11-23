"""
Boot Barn Scraper
Scrapes bootbarn.com for western apparel and gear.
"""

import re
from typing import List, Optional
from bs4 import BeautifulSoup
from .base_ecommerce import BaseEcommerceScraper, ProductData
import logging

logger = logging.getLogger(__name__)


class BootBarnScraper(BaseEcommerceScraper):
    """Scraper for bootbarn.com"""

    SITE_NAME = "boot_barn"
    BASE_URL = "https://www.bootbarn.com"

    CATEGORIES = {
        "boots": "/mens-boots",
        "womens_boots": "/womens-boots",
        "hats": "/mens-hats",
        "jeans": "/mens-jeans",
        "shirts": "/mens-shirts",
        "outerwear": "/mens-outerwear",
        "work_boots": "/work-boots",
        "kids": "/kids",
        "accessories": "/accessories",
        "tack": "/horse-tack"
    }

    BRANDS = [
        "ariat", "justin", "tony-lama", "lucchese", "corral", "dan-post",
        "durango", "twisted-x", "old-gringo", "roper", "laredo",
        "resistol", "stetson", "wrangler", "cinch", "ely-cattleman"
    ]

    async def scrape_product(self, url: str) -> Optional[ProductData]:
        """Scrape a single product page from Boot Barn."""
        html = await self.get_page_content(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Product name
            name_elem = soup.select_one('h1.product-name, h1[itemprop="name"]')
            name = name_elem.get_text(strip=True) if name_elem else ""

            # Brand
            brand_elem = soup.select_one('.product-brand, span[itemprop="brand"]')
            brand = brand_elem.get_text(strip=True) if brand_elem else ""

            # Price
            price_elem = soup.select_one('.price-sales, .product-price')
            price = self.parse_price(price_elem.get_text() if price_elem else "0")

            # Original price (if on sale)
            orig_price_elem = soup.select_one('.price-standard, .original-price')
            original_price = self.parse_price(orig_price_elem.get_text() if orig_price_elem else "")

            # SKU/Product ID
            sku_elem = soup.select_one('.product-id, [data-pid]')
            sku = sku_elem.get('data-pid') or sku_elem.get_text(strip=True) if sku_elem else ""

            # Rating
            rating_elem = soup.select_one('.rating-value, [itemprop="ratingValue"]')
            rating = float(rating_elem.get_text(strip=True)) if rating_elem else None

            # Review count
            review_elem = soup.select_one('.review-count, [itemprop="reviewCount"]')
            review_count = int(re.sub(r'\D', '', review_elem.get_text())) if review_elem else 0

            # Stock status
            stock_elem = soup.select_one('.in-stock, .availability')
            in_stock = bool(stock_elem and 'out' not in stock_elem.get_text().lower())

            # Sizes
            size_elems = soup.select('.size-swatch:not(.unavailable), .size-option:not(.disabled)')
            sizes = [s.get_text(strip=True) for s in size_elems]

            # Colors
            color_elems = soup.select('.color-swatch, .color-value')
            colors = [c.get('title') or c.get_text(strip=True) for c in color_elems]

            # Image
            img_elem = soup.select_one('.product-image img, img[itemprop="image"]')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else ""

            # Description
            desc_elem = soup.select_one('.product-description, [itemprop="description"]')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Category detection
            breadcrumb = soup.select('.breadcrumb a')
            category = breadcrumb[-2].get_text(strip=True) if len(breadcrumb) > 1 else "unknown"

            sale_price = price if original_price and original_price > price else None
            discount = self.calculate_discount(original_price, price) if original_price and sale_price else None

            return ProductData(
                product_id=sku or url.split('/')[-1],
                name=name,
                brand=brand,
                category=category,
                price=original_price or price,
                original_price=original_price,
                sale_price=sale_price,
                discount_percent=discount,
                in_stock=in_stock,
                sizes_available=sizes,
                colors_available=colors,
                url=url,
                image_url=image_url,
                description=description,
                sku=sku,
                rating=rating,
                review_count=review_count,
                source=self.SITE_NAME
            )

        except Exception as e:
            logger.error(f"Error parsing Boot Barn product: {e}")
            return None

    async def scrape_category(self, category: str, limit: int = 100) -> List[ProductData]:
        """Scrape all products from a category."""
        if category not in self.CATEGORIES:
            return []

        products = []
        page_num = 1
        category_path = self.CATEGORIES[category]

        while len(products) < limit:
            url = f"{self.BASE_URL}{category_path}?page={page_num}"
            html = await self.get_page_content(url)

            if not html:
                break

            soup = BeautifulSoup(html, 'html.parser')
            product_tiles = soup.select('.product-tile, .product-card')

            if not product_tiles:
                break

            for tile in product_tiles:
                if len(products) >= limit:
                    break

                try:
                    # Extract quick data from listing
                    link = tile.select_one('a.product-link, a[href*="/p/"]')
                    product_url = self.BASE_URL + link.get('href') if link else None

                    if not product_url:
                        continue

                    name_elem = tile.select_one('.product-name, .tile-title')
                    price_elem = tile.select_one('.price-sales, .product-price')
                    brand_elem = tile.select_one('.brand-name, .product-brand')
                    img_elem = tile.select_one('img')

                    products.append(ProductData(
                        product_id=product_url.split('/')[-1],
                        name=name_elem.get_text(strip=True) if name_elem else "",
                        brand=brand_elem.get_text(strip=True) if brand_elem else "",
                        category=category,
                        price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                        url=product_url,
                        image_url=img_elem.get('src') if img_elem else "",
                        source=self.SITE_NAME
                    ))

                except Exception as e:
                    logger.error(f"Error parsing product tile: {e}")
                    continue

            page_num += 1
            if page_num > 20:  # Safety limit
                break

        return products

    async def search_products(self, query: str, limit: int = 50) -> List[ProductData]:
        """Search Boot Barn products."""
        products = []
        url = f"{self.BASE_URL}/search?q={query.replace(' ', '+')}"

        html = await self.get_page_content(url)
        if not html:
            return products

        soup = BeautifulSoup(html, 'html.parser')
        product_tiles = soup.select('.product-tile, .product-card')[:limit]

        for tile in product_tiles:
            try:
                link = tile.select_one('a.product-link, a[href*="/p/"]')
                product_url = self.BASE_URL + link.get('href') if link else None

                if not product_url:
                    continue

                name_elem = tile.select_one('.product-name, .tile-title')
                price_elem = tile.select_one('.price-sales, .product-price')
                brand_elem = tile.select_one('.brand-name')

                products.append(ProductData(
                    product_id=product_url.split('/')[-1],
                    name=name_elem.get_text(strip=True) if name_elem else "",
                    brand=brand_elem.get_text(strip=True) if brand_elem else "",
                    category="search",
                    price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                    url=product_url,
                    source=self.SITE_NAME
                ))
            except Exception as e:
                logger.error(f"Error parsing search result: {e}")
                continue

        return products

    async def scrape_brand(self, brand: str, limit: int = 100) -> List[ProductData]:
        """Scrape all products from a specific brand."""
        brand_slug = brand.lower().replace(' ', '-')
        url = f"{self.BASE_URL}/brands/{brand_slug}"
        return await self.scrape_category_url(url, limit)

    async def scrape_category_url(self, url: str, limit: int = 100) -> List[ProductData]:
        """Scrape products from a direct category URL."""
        products = []
        page_num = 1

        while len(products) < limit:
            page_url = f"{url}?page={page_num}"
            html = await self.get_page_content(page_url)

            if not html:
                break

            soup = BeautifulSoup(html, 'html.parser')
            product_tiles = soup.select('.product-tile, .product-card')

            if not product_tiles:
                break

            for tile in product_tiles:
                if len(products) >= limit:
                    break

                try:
                    link = tile.select_one('a.product-link, a[href*="/p/"]')
                    product_url = self.BASE_URL + link.get('href') if link else None

                    if not product_url:
                        continue

                    name_elem = tile.select_one('.product-name, .tile-title')
                    price_elem = tile.select_one('.price-sales, .product-price')

                    products.append(ProductData(
                        product_id=product_url.split('/')[-1],
                        name=name_elem.get_text(strip=True) if name_elem else "",
                        brand="",
                        category="",
                        price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                        url=product_url,
                        source=self.SITE_NAME
                    ))
                except Exception:
                    continue

            page_num += 1
            if page_num > 20:
                break

        return products

    async def get_sale_items(self, limit: int = 100) -> List[ProductData]:
        """Get all items on sale."""
        return await self.scrape_category_url(f"{self.BASE_URL}/sale", limit)
