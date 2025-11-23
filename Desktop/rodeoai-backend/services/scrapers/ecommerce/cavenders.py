"""
Cavenders Scraper
Scrapes cavenders.com for western apparel and gear.
"""

import re
from typing import List, Optional
from bs4 import BeautifulSoup
from .base_ecommerce import BaseEcommerceScraper, ProductData
import logging

logger = logging.getLogger(__name__)


class CavendersScraper(BaseEcommerceScraper):
    """Scraper for cavenders.com"""

    SITE_NAME = "cavenders"
    BASE_URL = "https://www.cavenders.com"

    CATEGORIES = {
        "mens_boots": "/mens/boots",
        "womens_boots": "/womens/boots",
        "mens_hats": "/mens/hats",
        "womens_hats": "/womens/hats",
        "mens_jeans": "/mens/jeans",
        "mens_shirts": "/mens/shirts",
        "kids_boots": "/kids/boots",
        "work_boots": "/work/boots",
        "tack": "/tack-accessories"
    }

    async def scrape_product(self, url: str) -> Optional[ProductData]:
        """Scrape a single product page from Cavenders."""
        html = await self.get_page_content(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            name_elem = soup.select_one('h1.product-title, .pdp-title')
            name = name_elem.get_text(strip=True) if name_elem else ""

            brand_elem = soup.select_one('.product-brand, .brand-name')
            brand = brand_elem.get_text(strip=True) if brand_elem else ""

            price_elem = soup.select_one('.price-value, .current-price')
            price = self.parse_price(price_elem.get_text() if price_elem else "0")

            orig_elem = soup.select_one('.original-price, .was-price')
            original_price = self.parse_price(orig_elem.get_text() if orig_elem else "")

            sku_elem = soup.select_one('.product-sku, [data-product-id]')
            sku = sku_elem.get('data-product-id') or sku_elem.get_text(strip=True) if sku_elem else ""

            rating_elem = soup.select_one('.star-rating, [itemprop="ratingValue"]')
            rating = float(rating_elem.get('content', 0)) if rating_elem else None

            stock_elem = soup.select_one('.availability-msg, .stock-status')
            in_stock = bool(stock_elem and 'out' not in stock_elem.get_text().lower())

            size_elems = soup.select('.size-swatch:not(.disabled), .size-btn:not(.sold-out)')
            sizes = [s.get_text(strip=True) for s in size_elems]

            color_elems = soup.select('.color-swatch, .color-option')
            colors = [c.get('title', c.get_text(strip=True)) for c in color_elems]

            img_elem = soup.select_one('.product-image img, .gallery-image')
            image_url = img_elem.get('src') if img_elem else ""

            desc_elem = soup.select_one('.product-description, .pdp-description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            sale_price = price if original_price and original_price > price else None
            discount = self.calculate_discount(original_price, price) if original_price and sale_price else None

            return ProductData(
                product_id=sku or url.split('/')[-1],
                name=name,
                brand=brand,
                category="",
                price=original_price or price or 0,
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
                source=self.SITE_NAME
            )

        except Exception as e:
            logger.error(f"Error parsing Cavenders product: {e}")
            return None

    async def scrape_category(self, category: str, limit: int = 100) -> List[ProductData]:
        """Scrape products from category."""
        if category not in self.CATEGORIES:
            return []

        products = []
        page_num = 1
        path = self.CATEGORIES[category]

        while len(products) < limit:
            url = f"{self.BASE_URL}{path}?page={page_num}"
            html = await self.get_page_content(url)

            if not html:
                break

            soup = BeautifulSoup(html, 'html.parser')
            tiles = soup.select('.product-tile, .product-card, .product-item')

            if not tiles:
                break

            for tile in tiles:
                if len(products) >= limit:
                    break

                try:
                    link = tile.select_one('a[href*="/product/"], a.product-link')
                    href = link.get('href') if link else ""
                    product_url = href if href.startswith('http') else self.BASE_URL + href

                    name_elem = tile.select_one('.product-name, .tile-title')
                    price_elem = tile.select_one('.price, .product-price')
                    brand_elem = tile.select_one('.brand')

                    products.append(ProductData(
                        product_id=product_url.split('/')[-1] if product_url else "",
                        name=name_elem.get_text(strip=True) if name_elem else "",
                        brand=brand_elem.get_text(strip=True) if brand_elem else "",
                        category=category,
                        price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                        url=product_url,
                        source=self.SITE_NAME
                    ))
                except Exception as e:
                    logger.error(f"Error parsing tile: {e}")
                    continue

            page_num += 1
            if page_num > 20:
                break

        return products

    async def search_products(self, query: str, limit: int = 50) -> List[ProductData]:
        """Search Cavenders products."""
        products = []
        url = f"{self.BASE_URL}/search?q={query.replace(' ', '+')}"

        html = await self.get_page_content(url)
        if not html:
            return products

        soup = BeautifulSoup(html, 'html.parser')
        tiles = soup.select('.product-tile, .product-item')[:limit]

        for tile in tiles:
            try:
                link = tile.select_one('a[href]')
                href = link.get('href') if link else ""
                product_url = href if href.startswith('http') else self.BASE_URL + href

                name_elem = tile.select_one('.product-name')
                price_elem = tile.select_one('.price')

                products.append(ProductData(
                    product_id=product_url.split('/')[-1],
                    name=name_elem.get_text(strip=True) if name_elem else "",
                    brand="",
                    category="search",
                    price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                    url=product_url,
                    source=self.SITE_NAME
                ))
            except Exception:
                continue

        return products
