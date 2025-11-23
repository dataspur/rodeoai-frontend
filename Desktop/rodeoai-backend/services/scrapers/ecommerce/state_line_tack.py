"""
State Line Tack Scraper
Scrapes statelinetack.com for tack and equine equipment.
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from .base_ecommerce import BaseEcommerceScraper, ProductData
import logging

logger = logging.getLogger(__name__)


class StateLineTackScraper(BaseEcommerceScraper):
    """Scraper for statelinetack.com"""

    SITE_NAME = "state_line_tack"
    BASE_URL = "https://www.statelinetack.com"

    CATEGORIES = {
        "saddles": "/saddles",
        "western_saddles": "/western-saddles",
        "english_saddles": "/english-saddles",
        "bridles": "/bridles-headstalls",
        "bits": "/bits",
        "reins": "/reins",
        "halters": "/halters-leads",
        "blankets": "/horse-blankets",
        "boots_wraps": "/horse-boots-wraps",
        "grooming": "/grooming-supplies",
        "supplements": "/horse-supplements",
        "feed": "/horse-feed",
        "apparel": "/riding-apparel"
    }

    async def scrape_product(self, url: str) -> Optional[ProductData]:
        """Scrape single State Line Tack product."""
        html = await self.get_page_content(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            name_elem = soup.select_one('h1.product-name, .pdp-title')
            name = name_elem.get_text(strip=True) if name_elem else ""

            brand_elem = soup.select_one('.product-brand, .brand-link')
            brand = brand_elem.get_text(strip=True) if brand_elem else ""

            price_elem = soup.select_one('.product-price, .price-value')
            price = self.parse_price(price_elem.get_text() if price_elem else "0")

            orig_elem = soup.select_one('.price-standard, .was-price')
            original_price = self.parse_price(orig_elem.get_text() if orig_elem else "")

            sku_elem = soup.select_one('.product-sku, .item-number')
            sku = sku_elem.get_text(strip=True).replace('Item #:', '').strip() if sku_elem else ""

            rating_elem = soup.select_one('.rating-value, .bv-rating')
            rating = float(rating_elem.get_text(strip=True)[:3]) if rating_elem else None

            review_elem = soup.select_one('.review-count')
            review_count = int(''.join(filter(str.isdigit, review_elem.get_text()))) if review_elem else 0

            stock_elem = soup.select_one('.availability, .stock-message')
            in_stock = bool(stock_elem and 'out' not in stock_elem.get_text().lower())

            size_elems = soup.select('.size-swatch:not(.unavailable), .size-option')
            sizes = [s.get_text(strip=True) for s in size_elems]

            color_elems = soup.select('.color-swatch, .color-option')
            colors = [c.get('title', c.get_text(strip=True)) for c in color_elems]

            img_elem = soup.select_one('.product-image img, .gallery-image')
            image_url = img_elem.get('src') if img_elem else ""

            desc_elem = soup.select_one('.product-description, .description-content')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            sale_price = price if original_price and original_price > price else None

            return ProductData(
                product_id=sku or url.split('/')[-1],
                name=name,
                brand=brand,
                category="",
                price=original_price or price or 0,
                original_price=original_price,
                sale_price=sale_price,
                discount_percent=self.calculate_discount(original_price, price) if sale_price else None,
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
            logger.error(f"Error parsing State Line Tack product: {e}")
            return None

    async def scrape_category(self, category: str, limit: int = 100) -> List[ProductData]:
        """Scrape category."""
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
            tiles = soup.select('.product-tile, .product-item')

            if not tiles:
                break

            for tile in tiles:
                if len(products) >= limit:
                    break

                try:
                    link = tile.select_one('a[href*="/"]')
                    href = link.get('href') if link else ""
                    product_url = href if href.startswith('http') else self.BASE_URL + href

                    name_elem = tile.select_one('.product-name')
                    price_elem = tile.select_one('.product-price')
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
                except Exception:
                    continue

            page_num += 1
            if page_num > 20:
                break

        return products

    async def search_products(self, query: str, limit: int = 50) -> List[ProductData]:
        """Search products."""
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
                product_url = link.get('href') if link else ""

                name_elem = tile.select_one('.product-name')
                price_elem = tile.select_one('.product-price')

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
