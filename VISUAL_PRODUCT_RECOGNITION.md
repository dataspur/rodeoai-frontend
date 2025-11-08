# Visual Product Recognition & Price Intelligence System

## Overview

This document outlines the implementation of a visual product recognition system that can:
1. Identify products (boots, hats, vests, etc.) from photos within seconds
2. Determine exact brand, make, and model
3. Find lowest prices across hundreds of online stores
4. Track inventory status and sales/promotions
5. Extract photo metadata and fingerprint devices

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Upload                           │
│                    (Photo of Product)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Image Processing Pipeline                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ EXIF Extract │→ │ Device FP    │→ │ Image Prep   │      │
│  │ & Validation │  │ & Storage    │  │ & Enhancement│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Computer Vision & Product Recognition              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Category     │→ │ Brand        │→ │ Model        │      │
│  │ Detection    │  │ Recognition  │  │ Matching     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Technologies: YOLOv8, ResNet, Vision Transformer           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Product Database Matching                       │
│  ┌──────────────────────────────────────────────┐           │
│  │  PostgreSQL + pgvector for similarity search │           │
│  │  - Product catalog (1M+ items)               │           │
│  │  - Visual embeddings for each product        │           │
│  │  - Brand/model metadata                      │           │
│  └──────────────────────────────────────────────┘           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Price Intelligence Engine                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Redis Cache  │  │ Price Scraper│  │ Inventory    │      │
│  │ (Hot prices) │←─│ (Celery)     │←─│ Tracker      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Updates: Every 12 hours + real-time triggers               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Response to User                             │
│  {                                                           │
│    "product": {                                              │
│      "brand": "Ariat",                                       │
│      "model": "Heritage Roughstock Square Toe",              │
│      "category": "Western Boots",                            │
│      "confidence": 0.95                                      │
│    },                                                        │
│    "prices": [                                               │
│      {"store": "Boot Barn", "price": 189.99, "in_stock": true},│
│      {"store": "Sheplers", "price": 199.95, "sale": true}   │
│    ],                                                        │
│    "lowest_price": 189.99,                                   │
│    "match_time_ms": 1847                                     │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component 1: Image Processing & Metadata Extraction

### Photo Metadata Extraction

Extract EXIF data and create device fingerprint:

```python
# image_processor.py

from PIL import Image
from PIL.ExifTags import TAGS
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime
import imagehash

class ImageProcessor:
    """Process uploaded images, extract metadata, and create device fingerprints."""

    @staticmethod
    def extract_exif(image_path: str) -> Dict:
        """
        Extract EXIF metadata from image.

        Returns camera info, GPS coordinates, timestamps, etc.
        """
        try:
            image = Image.open(image_path)
            exif_data = {}

            # Get EXIF data
            exif = image._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)

            # Extract key metadata
            metadata = {
                "camera_make": exif_data.get("Make"),
                "camera_model": exif_data.get("Model"),
                "software": exif_data.get("Software"),
                "datetime_original": exif_data.get("DateTimeOriginal"),
                "gps_info": ImageProcessor._extract_gps(exif_data),
                "image_dimensions": {
                    "width": image.width,
                    "height": image.height
                },
                "format": image.format,
                "mode": image.mode,
                "lens_info": {
                    "focal_length": exif_data.get("FocalLength"),
                    "f_number": exif_data.get("FNumber"),
                    "iso": exif_data.get("ISOSpeedRatings"),
                },
                "orientation": exif_data.get("Orientation"),
                "flash": exif_data.get("Flash"),
            }

            return metadata

        except Exception as e:
            print(f"Error extracting EXIF: {e}")
            return {}

    @staticmethod
    def _extract_gps(exif_data: Dict) -> Optional[Dict]:
        """Extract GPS coordinates if available."""
        gps_info = exif_data.get("GPSInfo")
        if not gps_info:
            return None

        # Parse GPS data (simplified)
        return {
            "latitude": gps_info.get("GPSLatitude"),
            "longitude": gps_info.get("GPSLongitude"),
            "altitude": gps_info.get("GPSAltitude"),
        }

    @staticmethod
    def create_device_fingerprint(image_path: str, metadata: Dict) -> str:
        """
        Create unique device fingerprint from image metadata.

        Combines camera model, software, and image characteristics
        to create a consistent fingerprint for the same device.
        """
        # Create fingerprint from stable metadata
        fingerprint_data = {
            "camera_make": metadata.get("camera_make", ""),
            "camera_model": metadata.get("camera_model", ""),
            "software": metadata.get("software", ""),
            # Image processing characteristics
            "aspect_ratio": round(
                metadata["image_dimensions"]["width"] /
                metadata["image_dimensions"]["height"],
                2
            ),
        }

        # Create hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        device_id = hashlib.sha256(fingerprint_str.encode()).hexdigest()

        return device_id

    @staticmethod
    def create_image_hash(image_path: str) -> str:
        """
        Create perceptual hash of image for duplicate detection.
        """
        image = Image.open(image_path)

        # Use perceptual hashing (similar images = similar hashes)
        phash = imagehash.phash(image)

        return str(phash)

    @staticmethod
    def preprocess_for_recognition(image_path: str, output_path: str = None) -> str:
        """
        Prepare image for product recognition.
        - Resize to standard dimensions
        - Enhance quality
        - Remove background (optional)
        """
        image = Image.open(image_path)

        # Resize to standard size (keep aspect ratio)
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Auto-enhance
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)

        # Save processed image
        if output_path:
            image.save(output_path, quality=95)
            return output_path

        return image_path
```

### Database Model for Device Tracking

```python
# models.py (add to existing models)

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from database import Base

class DeviceFingerprint(Base):
    """Track devices uploading images."""
    __tablename__ = "device_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)

    # Device metadata
    camera_make = Column(String(100))
    camera_model = Column(String(100))
    software = Column(String(200))

    # Tracking
    first_seen = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen = Column(DateTime(timezone=True), default=datetime.utcnow)
    upload_count = Column(Integer, default=1)

    # Associated user (if authenticated)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Additional metadata
    metadata = Column(JSONB)

    __table_args__ = (
        Index('idx_device_user', 'device_id', 'user_id'),
    )


class ImageUpload(Base):
    """Track all image uploads."""
    __tablename__ = "image_uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(String(64), ForeignKey("device_fingerprints.device_id"))

    # Image info
    image_hash = Column(String(64), index=True)  # Perceptual hash
    file_path = Column(String(500))
    upload_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)

    # EXIF metadata
    exif_data = Column(JSONB)

    # GPS if available
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Recognition results (cached)
    recognition_results = Column(JSONB)
    processing_time_ms = Column(Integer)

    __table_args__ = (
        Index('idx_upload_device_time', 'device_id', 'upload_timestamp'),
        Index('idx_upload_hash', 'image_hash'),
    )


class ProductCatalog(Base):
    """Master product catalog."""
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, index=True)

    # Product identity
    brand = Column(String(100), index=True, nullable=False)
    model = Column(String(200), index=True, nullable=False)
    category = Column(String(50), index=True)  # boots, hats, vests, etc.
    subcategory = Column(String(100))

    # Product details
    description = Column(String(1000))
    sku = Column(String(100), unique=True)
    upc = Column(String(20), index=True)

    # Visual data
    image_urls = Column(JSONB)  # Array of product images
    visual_embedding = Column(String)  # Vector embedding for similarity search

    # Metadata
    attributes = Column(JSONB)  # Color, size, material, etc.
    keywords = Column(JSONB)  # Search keywords

    # Pricing (current best price - updated frequently)
    current_best_price = Column(Float)
    msrp = Column(Float)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_product_brand_model', 'brand', 'model'),
        Index('idx_product_category', 'category', 'subcategory'),
    )


class ProductPrice(Base):
    """Price history across different stores."""
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product_catalog.id"), index=True)

    # Store info
    store_name = Column(String(100), index=True)
    store_url = Column(String(500))
    product_url = Column(String(500))

    # Price data
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # If on sale
    is_on_sale = Column(Boolean, default=False)
    sale_end_date = Column(DateTime(timezone=True), nullable=True)

    # Availability
    in_stock = Column(Boolean, default=True)
    stock_level = Column(String(50))  # "low", "medium", "high", or actual number

    # Tracking
    scraped_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    last_verified = Column(DateTime(timezone=True))

    # Metadata
    shipping_info = Column(JSONB)  # Free shipping, delivery time, etc.

    __table_args__ = (
        Index('idx_price_product_store', 'product_id', 'store_name'),
        Index('idx_price_scraped', 'scraped_at'),
    )
```

## Component 2: Computer Vision & Product Recognition

### Product Recognition Service

```python
# product_recognition.py

from typing import Dict, List, Tuple, Optional
import torch
from PIL import Image
import numpy as np
from transformers import AutoImageProcessor, AutoModelForImageClassification
from transformers import CLIPProcessor, CLIPModel
import cv2

class ProductRecognitionService:
    """
    Multi-stage product recognition:
    1. Category detection (boots, hats, vests, etc.)
    2. Brand recognition
    3. Model matching via visual similarity
    """

    def __init__(self):
        """Initialize models."""

        # Stage 1: Category classifier (fine-tuned on western wear)
        self.category_processor = AutoImageProcessor.from_pretrained(
            "google/vit-base-patch16-224"
        )
        self.category_model = AutoModelForImageClassification.from_pretrained(
            "models/category_classifier"  # Your fine-tuned model
        )

        # Stage 2: CLIP for brand/product matching
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

        # Category labels
        self.categories = [
            "cowboy_boots", "cowboy_hat", "western_vest",
            "equestrian_vest", "riding_boots", "belt_buckle",
            "saddle", "chaps", "other"
        ]

        # Major brands to recognize
        self.brands = [
            "Ariat", "Justin Boots", "Lucchese", "Tony Lama",
            "Stetson", "Resistol", "American Hat Company",
            "Cinch", "Wrangler", "Cripple Creek", "Scully"
        ]

    def recognize_product(
        self,
        image_path: str
    ) -> Dict:
        """
        Full product recognition pipeline.

        Returns:
            {
                "category": "cowboy_boots",
                "confidence": 0.95,
                "brand": "Ariat",
                "brand_confidence": 0.87,
                "top_matches": [
                    {
                        "product_id": 12345,
                        "brand": "Ariat",
                        "model": "Heritage Roughstock",
                        "similarity": 0.92,
                        "image_url": "..."
                    },
                    ...
                ],
                "processing_time_ms": 1234
            }
        """
        import time
        start_time = time.time()

        # Load image
        image = Image.open(image_path).convert("RGB")

        # Stage 1: Detect category
        category, category_conf = self._detect_category(image)

        # Stage 2: Detect brand
        brand, brand_conf = self._detect_brand(image, category)

        # Stage 3: Find similar products
        top_matches = self._find_similar_products(image, category, brand)

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "category": category,
            "category_confidence": category_conf,
            "brand": brand,
            "brand_confidence": brand_conf,
            "top_matches": top_matches,
            "processing_time_ms": processing_time
        }

    def _detect_category(self, image: Image.Image) -> Tuple[str, float]:
        """Detect product category."""
        inputs = self.category_processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self.category_model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)

            top_prob, top_idx = torch.max(probs, dim=1)

            category = self.categories[top_idx.item()]
            confidence = top_prob.item()

        return category, confidence

    def _detect_brand(self, image: Image.Image, category: str) -> Tuple[str, float]:
        """
        Detect brand using CLIP zero-shot classification.
        """
        # Create text prompts for each brand
        prompts = [f"a photo of {brand} {category.replace('_', ' ')}"
                   for brand in self.brands]

        # Process image and text
        inputs = self.clip_processor(
            text=prompts,
            images=image,
            return_tensors="pt",
            padding=True
        )

        with torch.no_grad():
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

            top_prob, top_idx = torch.max(probs, dim=1)

            brand = self.brands[top_idx.item()]
            confidence = top_prob.item()

        return brand, confidence

    def _find_similar_products(
        self,
        image: Image.Image,
        category: str,
        brand: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find visually similar products from catalog.

        Uses CLIP embeddings + vector similarity search.
        """
        # Generate image embedding
        inputs = self.clip_processor(images=image, return_tensors="pt")

        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
            image_embedding = image_features / image_features.norm(dim=-1, keepdim=True)
            image_embedding = image_embedding.cpu().numpy()[0]

        # Query database for similar products
        # (This would use pgvector in production)
        from database import get_db
        from models import ProductCatalog

        db = next(get_db())

        # Filter by category and optionally brand
        query = db.query(ProductCatalog).filter(
            ProductCatalog.category == category
        )

        if brand:
            query = query.filter(ProductCatalog.brand == brand)

        products = query.limit(100).all()  # Get candidates

        # Calculate similarity scores
        matches = []
        for product in products:
            if not product.visual_embedding:
                continue

            # Convert stored embedding back to numpy
            product_embedding = np.array(eval(product.visual_embedding))

            # Cosine similarity
            similarity = float(np.dot(image_embedding, product_embedding))

            matches.append({
                "product_id": product.id,
                "brand": product.brand,
                "model": product.model,
                "category": product.category,
                "similarity": similarity,
                "image_url": product.image_urls[0] if product.image_urls else None,
                "current_price": product.current_best_price,
                "description": product.description
            })

        # Sort by similarity
        matches.sort(key=lambda x: x["similarity"], reverse=True)

        return matches[:top_k]

    def generate_product_embedding(self, image_path: str) -> List[float]:
        """
        Generate visual embedding for a product image.
        Used when adding products to catalog.
        """
        image = Image.open(image_path).convert("RGB")
        inputs = self.clip_processor(images=image, return_tensors="pt")

        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
            embedding = image_features / image_features.norm(dim=-1, keepdim=True)
            embedding = embedding.cpu().numpy()[0].tolist()

        return embedding
```

### API Endpoint for Product Recognition

```python
# main.py (add to existing endpoints)

from fastapi import File, UploadFile, BackgroundTasks
from product_recognition import ProductRecognitionService
from image_processor import ImageProcessor
from price_intelligence import PriceIntelligenceService
import tempfile
import os

# Initialize services
product_recognition = ProductRecognitionService()
price_intelligence = PriceIntelligenceService()

@app.post("/api/recognize-product")
@limiter.limit("10/minute")
async def recognize_product(
    request: Request,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Upload photo and get product identification + pricing.

    Returns:
        - Product category, brand, model
        - Top matching products
        - Current prices from multiple stores
        - Inventory status
        - Device fingerprint (stored)
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Extract metadata and create device fingerprint
        metadata = ImageProcessor.extract_exif(tmp_path)
        device_id = ImageProcessor.create_device_fingerprint(tmp_path, metadata)
        image_hash = ImageProcessor.create_image_hash(tmp_path)

        # Store or update device fingerprint
        device = db.query(DeviceFingerprint).filter(
            DeviceFingerprint.device_id == device_id
        ).first()

        if device:
            device.last_seen = datetime.utcnow()
            device.upload_count += 1
        else:
            device = DeviceFingerprint(
                device_id=device_id,
                camera_make=metadata.get("camera_make"),
                camera_model=metadata.get("camera_model"),
                software=metadata.get("software"),
                user_id=current_user.id if current_user else None,
                metadata=metadata
            )
            db.add(device)

        db.commit()

        # Preprocess image for recognition
        processed_path = ImageProcessor.preprocess_for_recognition(tmp_path)

        # Run product recognition
        recognition_result = product_recognition.recognize_product(processed_path)

        # Get pricing for top matches
        if recognition_result["top_matches"]:
            top_product = recognition_result["top_matches"][0]
            pricing = price_intelligence.get_product_prices(
                product_id=top_product["product_id"],
                limit=10
            )

            recognition_result["pricing"] = pricing

        # Store image upload record
        image_upload = ImageUpload(
            user_id=current_user.id if current_user else None,
            device_id=device_id,
            image_hash=image_hash,
            file_path=tmp_path,  # In production, upload to S3/cloud storage
            exif_data=metadata,
            latitude=metadata.get("gps_info", {}).get("latitude") if metadata.get("gps_info") else None,
            longitude=metadata.get("gps_info", {}).get("longitude") if metadata.get("gps_info") else None,
            recognition_results=recognition_result,
            processing_time_ms=recognition_result["processing_time_ms"]
        )
        db.add(image_upload)
        db.commit()

        # Clean up temp file (in background)
        if background_tasks:
            background_tasks.add_task(os.unlink, tmp_path)

        return {
            "success": True,
            "device_id": device_id,
            "upload_id": image_upload.id,
            "recognition": recognition_result
        }

    except Exception as e:
        print(f"Error in product recognition: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
```

This is just Part 1 of the implementation. Let me continue with the price scraping infrastructure...
