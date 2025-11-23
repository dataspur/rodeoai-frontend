"""
Wrangler Scraper
Scrapes wrangler.com for western apparel.
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from .base_ecommerce import BaseEcommerceScraper, ProductData
import logging

logger = logging.getLogger(__name__)


class WranglerScraper(BaseEcommerceScraper):
    """Scraper for wrangler.com"""

    SITE_NAME = "wrangler"
    BASE_URL = "https://www.wrangler.com"

    CATEGORIES = {
        "mens_jeans": "/shop/men/jeans",
        "mens_shirts": "/shop/men/shirts",
        "mens_outerwear": "/shop/men/outerwear",
        "womens_jeans": "/shop/women/jeans",
        "womens_tops": "/shop/women/tops",
        "kids": "/shop/kids",
        "western": "/shop/western",
        "retro": "/shop/retro",
        "cowboy_cut": "/shop/cowboy-cut"
    }

    async def scrape_product(self, url: str) -> Optional[ProductData]:
        """Scrape single Wrangler product."""
        html = await self.get_page_content(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            name_elem = soup.select_one('h1.product-name, .pdp-title')
            name = name_elem.get_text(strip=True) if name_elem else ""

            price_elem = soup.select_one('.product-price, .price-value')
            price = self.parse_price(price_elem.get_text() if price_elem else "0")

            orig_elem = soup.select_one('.price-standard, .original-price')
            original_price = self.parse_price(orig_elem.get_text() if orig_elem else "")

            sku_elem = soup.select_one('.product-id, .style-number')
            sku = sku_elem.get_text(strip=True) if sku_elem else ""

            rating_elem = soup.select_one('.bv-rating, [itemprop="ratingValue"]')
            rating = float(rating_elem.get_text(strip=True)[:3]) if rating_elem else None

            stock_elem = soup.select_one('.availability, .stock-status')
            in_stock = bool(stock_elem and 'out' not in stock_elem.get_text().lower())

            # Jeans specific: waist/inseam
            waist_elems = soup.select('.waist-option:not(.unavailable)')
            waists = [w.get_text(strip=True) for w in waist_elems]

            inseam_elems = soup.select('.inseam-option:not(.unavailable)')
            inseams = [i.get_text(strip=True) for i in inseam_elems]

            color_elems = soup.select('.color-swatch, .color-option')
            colors = [c.get('title', c.get_text(strip=True)) for c in color_elems]

            img_elem = soup.select_one('.product-image img')
            image_url = img_elem.get('src') if img_elem else ""

            desc_elem = soup.select_one('.product-description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Combine waist/inseam as sizes
            sizes = waists if waists else []
            if inseams:
                sizes.extend([f"Inseam: {i}" for i in inseams])

            sale_price = price if original_price and original_price > price else None

            return ProductData(
                product_id=sku or url.split('/')[-1],
                name=name,
                brand="Wrangler",
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
                source=self.SITE_NAME
            )

        except Exception as e:
            logger.error(f"Error parsing Wrangler product: {e}")
            return None

    async def scrape_category(self, category: str, limit: int = 100) -> List[ProductData]:
        """Scrape Wrangler category."""
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
            tiles = soup.select('.product-tile, .product-card')

            if not tiles:
                break

            for tile in tiles:
                if len(products) >= limit:
                    break

                try:
                    link = tile.select_one('a[href*="/shop/"]')
                    href = link.get('href') if link else ""
                    product_url = href if href.startswith('http') else self.BASE_URL + href

                    name_elem = tile.select_one('.product-name')
                    price_elem = tile.select_one('.product-price')

                    products.append(ProductData(
                        product_id=product_url.split('/')[-1] if product_url else "",
                        name=name_elem.get_text(strip=True) if name_elem else "",
                        brand="Wrangler",
                        category=category,
                        price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                        url=product_url,
                        source=self.SITE_NAME
                    ))
                except Exception:
                    continue

            page_num += 1
            if page_num > 15:
                break

        return products

    async def search_products(self, query: str, limit: int = 50) -> List[ProductData]:
        """Search Wrangler products."""
        products = []
        url = f"{self.BASE_URL}/search?q={query.replace(' ', '+')}"

        html = await self.get_page_content(url)
        if not html:
            return products

        soup = BeautifulSoup(html, 'html.parser')
        tiles = soup.select('.product-tile')[:limit]

        for tile in tiles:
            try:
                link = tile.select_one('a[href]')
                product_url = link.get('href') if link else ""

                name_elem = tile.select_one('.product-name')
                price_elem = tile.select_one('.product-price')

                products.append(ProductData(
                    product_id=product_url.split('/')[-1],
                    name=name_elem.get_text(strip=True) if name_elem else "",
                    brand="Wrangler",
                    category="search",
                    price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                    url=product_url,
                    source=self.SITE_NAME
                ))
            except Exception:
                continue

        return products
