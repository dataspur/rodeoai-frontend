# Visual Product Recognition - Implementation Roadmap

## Legal & Ethical Considerations ⚠️

### Web Scraping Legality

**CRITICAL: Web scraping has legal and ethical implications that must be addressed:**

#### 1. Robots.txt Compliance
- **Always respect** `robots.txt` files
- Check each store's robots.txt before scraping
- Many stores explicitly disallow scraping

```python
# Check robots.txt before scraping
import urllib.robotparser

def can_scrape(url: str) -> bool:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url + "/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)
```

#### 2. Terms of Service
- Review each store's Terms of Service
- Many explicitly prohibit automated data collection
- Violating ToS can lead to:
  - Legal action
  - IP bans
  - Cease & desist letters

#### 3. Legal Precedents
**Important Cases:**
- **hiQ Labs v. LinkedIn (2019)**: Scraping publicly available data may be legal
- **QVC v. Resultly (2018)**: Price scraping can be trademark infringement
- **GDPR & Privacy**: EU regulations on data collection

**Recommendation:**
- Consult with legal counsel before implementing scraping
- Consider partner APIs instead
- Use affiliate networks where possible

### Alternative Legal Approaches

#### Option 1: Affiliate Networks (RECOMMENDED)
Use affiliate APIs instead of scraping:

```python
# Example: CJ Affiliate Network API

import requests

class AffiliateAPI:
    """Use affiliate network APIs for price data."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://product-search.api.cj.com/v2"

    def search_product(self, keywords: str) -> List[Dict]:
        """Search products via affiliate API."""
        response = requests.get(
            f"{self.base_url}/product-search",
            headers={"authorization": f"Bearer {self.api_key}"},
            params={
                "keywords": keywords,
                "advertiser-ids": "joined",  # Only your partners
                "records-per-page": 100
            }
        )

        if response.status_code == 200:
            data = response.json()
            return self._parse_products(data)

        return []

    def _parse_products(self, data: Dict) -> List[Dict]:
        """Parse affiliate API response."""
        products = []

        for product in data.get("products", []):
            products.append({
                "name": product.get("name"),
                "price": product.get("price"),
                "url": product.get("link"),  # Affiliate link
                "advertiser": product.get("advertiser-name"),
                "in_stock": product.get("in-stock") == "yes",
                "image_url": product.get("image-url"),
                "upc": product.get("upc")
            })

        return products
```

**Benefits:**
- ✅ Legal and compliant
- ✅ Real-time data
- ✅ Earn commission on sales
- ✅ No scraping infrastructure needed

**Major Affiliate Networks:**
- Commission Junction (CJ)
- ShareASale
- Impact
- Pepperjam
- Amazon Associates

#### Option 2: Store APIs
Many stores offer official APIs:

- **Shopify Stores**: Use Shopify Admin API
- **WooCommerce**: REST API available
- **Amazon**: Product Advertising API
- **eBay**: Finding API

#### Option 3: Data Partnerships
- License price data from aggregators
- Partner directly with stores
- Use price comparison services APIs

### Device Fingerprinting Privacy

**GDPR & Privacy Laws:**
- Device fingerprinting may require user consent (GDPR)
- Clearly disclose data collection in privacy policy
- Provide opt-out mechanism
- Don't use for tracking without consent

**Compliant Approach:**
```python
# Get explicit consent before fingerprinting

@app.post("/api/recognize-product")
async def recognize_product(
    file: UploadFile,
    consent_to_fingerprinting: bool = False,  # Require explicit consent
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    # Extract metadata
    metadata = ImageProcessor.extract_exif(image_path)

    # Only create fingerprint if user consented
    if consent_to_fingerprinting:
        device_id = ImageProcessor.create_device_fingerprint(image_path, metadata)
        # Store fingerprint
    else:
        device_id = None

    # Continue with recognition...
```

## Implementation Phases

### Phase 1: Product Recognition (Weeks 1-4)

**Priority: High | Complexity: Medium | Cost: $$**

#### Week 1: Infrastructure Setup
- [ ] Set up image storage (AWS S3 or CloudFlare R2)
- [ ] Add database tables (DeviceFingerprint, ImageUpload, ProductCatalog)
- [ ] Install computer vision dependencies
- [ ] Create image processing pipeline

```bash
pip install torch torchvision pillow
pip install transformers sentence-transformers
pip install opencv-python imagehash
pip install boto3  # For S3
```

#### Week 2: Category Detection
- [ ] Collect training dataset (boots, hats, vests images)
- [ ] Fine-tune Vision Transformer (ViT) for category classification
- [ ] Achieve >90% accuracy on test set
- [ ] Deploy model

**Dataset Sources:**
- Scrape product images from stores (legal if publicly available)
- Use existing datasets (Fashion-MNIST, DeepFashion)
- Manual labeling (hire annotators on Scale AI or Labelbox)

#### Week 3: Brand Recognition
- [ ] Implement CLIP-based brand detection
- [ ] Create brand embedding database
- [ ] Test with sample images
- [ ] Optimize for speed (<2 seconds per image)

#### Week 4: Product Matching
- [ ] Build product catalog with visual embeddings
- [ ] Implement similarity search (pgvector)
- [ ] Create API endpoint
- [ ] Test end-to-end pipeline

**Deliverable:** Working product recognition from photos

### Phase 2: Product Catalog (Weeks 5-8)

**Priority: High | Complexity: High | Cost: $$$**

#### Catalog Building Strategy

**Option A: Manual Curation (Higher Quality)**
- Manually add top 1,000 products
- Focus on popular brands
- Include multiple images per product
- Generate visual embeddings

**Option B: Automated Scraping (Larger Scale)**
- Scrape product listings from stores
- Automated image download
- Automated embedding generation
- Manual quality check

**Option C: Data Licensing (Fastest)**
- License product data from:
  - GS1 Global (product database)
  - Semantics3 (product catalog API)
  - DataSift (retail data)

#### Week 5-6: Catalog Foundation
- [ ] Design catalog schema
- [ ] Build ingestion pipeline
- [ ] Add first 100 products manually
- [ ] Generate embeddings

#### Week 7-8: Scale Catalog
- [ ] Expand to 1,000+ products
- [ ] Add UPC/EAN codes
- [ ] Link products to stores
- [ ] Quality assurance

**Deliverable:** 1,000+ product catalog with embeddings

### Phase 3: Price Aggregation (Weeks 9-16)

**Priority: Medium | Complexity: Very High | Cost: $$$$**

⚠️ **IMPORTANT: Only proceed if legal approach determined**

#### Legal Compliance First
- [ ] Consult with attorney specialized in e-commerce law
- [ ] Review robots.txt for target stores
- [ ] Review Terms of Service
- [ ] Determine legal approach:
  - Affiliate APIs (RECOMMENDED)
  - Official store APIs
  - Licensed data
  - Scraping (if legally sound)

#### Week 9-10: Affiliate Network Integration
**If using affiliate approach:**

- [ ] Apply to affiliate networks:
  - Commission Junction
  - ShareASale
  - Impact
  - Amazon Associates

- [ ] Get approved by stores
- [ ] Implement affiliate APIs
- [ ] Build price database

```python
# Affiliate integration example

class PriceAggregator:
    def __init__(self):
        self.cj_api = CJAffiliateAPI(os.getenv("CJ_API_KEY"))
        self.shareasale_api = ShareASaleAPI(os.getenv("SHAREASALE_API_KEY"))
        self.amazon_api = AmazonAPI(os.getenv("AMAZON_KEY"))

    def get_prices(self, upc: str) -> List[Dict]:
        prices = []

        # Query each affiliate network
        prices.extend(self.cj_api.search_by_upc(upc))
        prices.extend(self.shareasale_api.search_by_upc(upc))
        prices.extend(self.amazon_api.search_by_upc(upc))

        return sorted(prices, key=lambda x: x["price"])
```

#### Week 11-12: Price Database
- [ ] Create price tracking database
- [ ] Implement caching layer (Redis)
- [ ] Build price history tracking
- [ ] Create price update pipeline

#### Week 13-14: Inventory Tracking
- [ ] Track stock status
- [ ] Detect when products go out of stock
- [ ] Implement low-stock alerts
- [ ] Build stock notification system

#### Week 15-16: Sale Detection
- [ ] Identify price drops
- [ ] Detect promotional periods
- [ ] Create sale alerts
- [ ] Build user notification system

**Deliverable:** Real-time price comparison across multiple stores

### Phase 4: Photo Metadata & Analytics (Weeks 17-18)

**Priority: Low | Complexity: Low | Cost: $**

#### Week 17: Metadata Extraction
- [ ] EXIF data extraction
- [ ] GPS coordinate parsing
- [ ] Device fingerprinting
- [ ] Privacy compliance checks

#### Week 18: Analytics Dashboard
- [ ] Upload analytics
- [ ] Device tracking (with consent)
- [ ] Popular product insights
- [ ] Search pattern analysis

**Deliverable:** Photo metadata extraction and analytics

## Infrastructure Requirements

### Hosting & Services

#### Compute
```
Production Environment:

Web Servers:
- 2x Application servers (FastAPI)
  AWS EC2 t3.large or equivalent
  Cost: ~$150/month

Background Workers (Celery):
- 4x Worker instances for scraping/processing
  AWS EC2 t3.medium
  Cost: ~$200/month

GPU for Computer Vision:
- 1x GPU instance for model inference
  AWS EC2 g4dn.xlarge (NVIDIA T4)
  Cost: ~$400/month
  OR use AWS Lambda with GPU for serverless

Database:
- PostgreSQL (with pgvector extension)
  AWS RDS db.t3.large
  Cost: ~$200/month

Cache/Queue:
- Redis (for caching + Celery broker)
  AWS ElastiCache t3.medium
  Cost: ~$80/month

Storage:
- S3 for image storage (100GB/month)
  Cost: ~$25/month

CDN:
- CloudFlare (free tier sufficient to start)
  Cost: $0

Total Infrastructure: ~$1,055/month
```

#### AI/ML Services
```
OpenAI API (for embeddings):
- 1M tokens/month for embeddings
  Cost: ~$20/month

Computer Vision Models:
- Self-hosted (included in GPU instance)
  OR
- AWS Rekognition Custom Labels
  Cost: ~$300/month
```

#### Web Scraping (if pursuing)
```
Proxy Services:
- Bright Data or Smartproxy
- 50GB residential proxies
  Cost: ~$500/month

Captcha Solving:
- 2Captcha or AntiCaptcha
  Cost: ~$100/month

Total Scraping: ~$600/month
(Avoid if using affiliate APIs instead)
```

### Total Monthly Costs

**Option A: With Affiliate APIs (RECOMMENDED)**
- Infrastructure: $1,055
- AI Services: $320
- **Total: ~$1,375/month**

**Option B: With Web Scraping (Legal review required)**
- Infrastructure: $1,055
- AI Services: $320
- Scraping: $600
- Legal counsel: $500+
- **Total: ~$2,475+/month**

### Development Time

**Full-Time Developer (1 person):**
- Phase 1 (Product Recognition): 4 weeks
- Phase 2 (Product Catalog): 4 weeks
- Phase 3 (Price Aggregation): 8 weeks
- Phase 4 (Metadata & Analytics): 2 weeks

**Total: 18 weeks (~4.5 months)**

**Team of 3:**
- Product Recognition: 2 weeks
- Catalog Building: 2 weeks
- Price System: 4 weeks
- Testing & QA: 1 week

**Total: 9 weeks (~2 months)**

## Alternative: Hybrid Approach

### Use Existing Services

Instead of building everything from scratch:

#### 1. Google Lens API (Product Recognition)
```python
from google.cloud import vision

def recognize_product_google(image_path: str) -> List[Dict]:
    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    response = client.product_search(image=image)

    products = []
    for result in response.results:
        products.append({
            "product": result.product,
            "score": result.score,
            "image": result.image
        })

    return products
```

**Cost:** $1.50 per 1,000 images

#### 2. Price Comparison APIs
Use existing services:
- **PriceAPI**: E-commerce price tracking API
- **Rainforest API**: Amazon product data
- **SerpAPI**: Google Shopping results

```python
import requests

def get_prices_priceapi(product_name: str) -> List[Dict]:
    response = requests.get(
        "https://api.priceapi.com/v2/jobs",
        headers={"x-api-key": os.getenv("PRICE_API_KEY")},
        json={
            "source": "google_shopping",
            "query": product_name,
            "country": "us"
        }
    )

    return response.json()
```

**Cost:** $20-200/month depending on volume

#### 3. Hybrid Implementation
- **Product Recognition**: Build custom (better accuracy for western wear)
- **Price Comparison**: Use APIs (legal, reliable, updated)
- **Metadata**: Build custom (simple to implement)

**Benefits:**
- Faster time to market (6-8 weeks vs 18 weeks)
- Lower legal risk
- Reduced infrastructure costs
- Focus on core product features

## Recommendations

### Short-Term (MVP - 2 months)

1. **Product Recognition**
   - Build custom computer vision model
   - Focus on top 20 brands
   - Support boots, hats, vests only
   - Target 85% accuracy

2. **Price Comparison**
   - Use affiliate network APIs
   - Partner with 5-10 major stores
   - Real-time pricing
   - Earn affiliate commissions

3. **Photo Upload**
   - Basic EXIF extraction
   - Optional device fingerprinting (with consent)
   - Store for analytics

**Launch MVP in 8 weeks with legal compliance**

### Long-Term (6-12 months)

1. **Expand Recognition**
   - Add more product categories
   - Improve accuracy to >95%
   - Support more brands
   - Add barcode/UPC scanning

2. **Advanced Price Features**
   - Price history & trends
   - Price drop alerts
   - Stock notifications
   - Best time to buy predictions

3. **Social Features**
   - Users can submit products
   - Community product database
   - Share finds
   - Reviews & ratings

## Next Steps

1. **Legal Review** (Week 1)
   - Consult attorney
   - Determine legal approach for price data
   - Draft privacy policy for device fingerprinting

2. **Partner Signup** (Week 1-2)
   - Apply to affiliate networks
   - Get approved by stores
   - Set up API access

3. **Infrastructure Setup** (Week 2)
   - Provision servers
   - Set up databases
   - Configure S3/storage
   - Install dependencies

4. **Model Training** (Week 3-4)
   - Collect training data
   - Train category classifier
   - Fine-tune brand recognition
   - Test accuracy

5. **Build Catalog** (Week 5-6)
   - Add first 100 products
   - Generate embeddings
   - Test matching accuracy

6. **Integrate Pricing** (Week 7-8)
   - Connect affiliate APIs
   - Build price database
   - Create caching layer
   - Test end-to-end

7. **Launch MVP** (Week 9)
   - Deploy to production
   - Monitor performance
   - Gather user feedback
   - Iterate

## Success Metrics

**Product Recognition:**
- Recognition accuracy: >85%
- Average response time: <3 seconds
- Top-5 match accuracy: >95%

**Price Comparison:**
- Store coverage: 10+ stores
- Price freshness: <24 hours
- Price accuracy: >99%

**User Engagement:**
- Upload-to-purchase rate: >5%
- Affiliate conversion rate: >2%
- User retention: >30% monthly

---

This is an ambitious but achievable project. The key decisions are:
1. Legal approach to price data (affiliate vs scraping)
2. Build vs buy for product recognition
3. MVP scope (start small, scale up)

I recommend starting with the affiliate API approach for legal compliance and faster time-to-market.
