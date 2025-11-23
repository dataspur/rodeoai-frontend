"""
Ariat Scraper
Scrapes ariat.com for boots and western apparel.
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from .base_ecommerce import BaseEcommerceScraper, ProductData
import logging

logger = logging.getLogger(__name__)


class AriatScraper(BaseEcommerceScraper):
    """Scraper for ariat.com"""

    SITE_NAME = "ariat"
    BASE_URL = "https://www.ariat.com"

    CATEGORIES = {
        "mens_boots": "/en/Men/Footwear/Cowboy-Boots",
        "womens_boots": "/en/Women/Footwear/Cowboy-Boots",
        "work_boots": "/en/Work/Footwear",
        "mens_apparel": "/en/Men/Clothing",
        "womens_apparel": "/en/Women/Clothing",
        "kids_boots": "/en/Kids/Footwear",
        "riding_boots": "/en/English/Footwear"
    }

    async def scrape_product(self, url: str) -> Optional[ProductData]:
        """Scrape single Ariat product."""
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

            sku_elem = soup.select_one('.product-id, [data-product-id]')
            sku = sku_elem.get('data-product-id') or sku_elem.get_text(strip=True) if sku_elem else ""

            rating_elem = soup.select_one('.bv-rating, [itemprop="ratingValue"]')
            rating = float(rating_elem.get_text(strip=True)[:3]) if rating_elem else None

            review_elem = soup.select_one('.bv-rating-count, [itemprop="reviewCount"]')
            review_count = int(''.join(filter(str.isdigit, review_elem.get_text()))) if review_elem else 0

            stock_elem = soup.select_one('.availability, .in-stock-msg')
            in_stock = bool(stock_elem and 'out' not in stock_elem.get_text().lower())

            size_elems = soup.select('.size-attribute:not(.unselectable), .size-btn:not(.disabled)')
            sizes = [s.get_text(strip=True) for s in size_elems]

            width_elems = soup.select('.width-attribute:not(.unselectable)')
            widths = [w.get_text(strip=True) for w in width_elems]

            img_elem = soup.select_one('.product-primary-image img, .pdp-image')
            image_url = img_elem.get('src') if img_elem else ""

            desc_elem = soup.select_one('.product-description, .pdp-description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Ariat specific: Technology features
            tech_elems = soup.select('.product-technology, .tech-badge')
            technologies = [t.get_text(strip=True) for t in tech_elems]

            sale_price = price if original_price and original_price > price else None

            return ProductData(
                product_id=sku or url.split('/')[-1].split('.')[0],
                name=name,
                brand="Ariat",
                category="",
                price=original_price or price or 0,
                original_price=original_price,
                sale_price=sale_price,
                discount_percent=self.calculate_discount(original_price, price) if sale_price else None,
                in_stock=in_stock,
                sizes_available=sizes,
                colors_available=widths,  # Using for widths
                url=url,
                image_url=image_url,
                description=description + " | Technologies: " + ", ".join(technologies) if technologies else description,
                sku=sku,
                rating=rating,
                review_count=review_count,
                source=self.SITE_NAME
            )

        except Exception as e:
            logger.error(f"Error parsing Ariat product: {e}")
            return None

    async def scrape_category(self, category: str, limit: int = 100) -> List[ProductData]:
        """Scrape Ariat category."""
        if category not in self.CATEGORIES:
            return []

        products = []
        page_num = 0
        path = self.CATEGORIES[category]

        while len(products) < limit:
            url = f"{self.BASE_URL}{path}?start={page_num * 24}&sz=24"
            html = await self.get_page_content(url)

            if not html:
                break

            soup = BeautifulSoup(html, 'html.parser')
            tiles = soup.select('.product-tile, .product-grid-item')

            if not tiles:
                break

            for tile in tiles:
                if len(products) >= limit:
                    break

                try:
                    link = tile.select_one('a.product-link, a[href*="/p/"]')
                    href = link.get('href') if link else ""
                    product_url = href if href.startswith('http') else self.BASE_URL + href

                    name_elem = tile.select_one('.product-name, .pdp-link')
                    price_elem = tile.select_one('.product-price, .price')

                    products.append(ProductData(
                        product_id=product_url.split('/')[-1].split('.')[0] if product_url else "",
                        name=name_elem.get_text(strip=True) if name_elem else "",
                        brand="Ariat",
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
        """Search Ariat products."""
        products = []
        url = f"{self.BASE_URL}/en/search?q={query.replace(' ', '+')}"

        html = await self.get_page_content(url)
        if not html:
            return products

        soup = BeautifulSoup(html, 'html.parser')
        tiles = soup.select('.product-tile')[:limit]

        for tile in tiles:
            try:
                link = tile.select_one('a[href]')
                href = link.get('href') if link else ""
                product_url = href if href.startswith('http') else self.BASE_URL + href

                name_elem = tile.select_one('.product-name')
                price_elem = tile.select_one('.product-price')

                products.append(ProductData(
                    product_id=product_url.split('/')[-1].split('.')[0],
                    name=name_elem.get_text(strip=True) if name_elem else "",
                    brand="Ariat",
                    category="search",
                    price=self.parse_price(price_elem.get_text() if price_elem else "0") or 0,
                    url=product_url,
                    source=self.SITE_NAME
                ))
            except Exception:
                continue

        return products
