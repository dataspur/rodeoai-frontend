"""
Product Recognition Service for Visual Search.

Handles:
- Category detection (boots, hats, vests, etc.)
- Brand recognition
- Model matching via visual similarity
- Integration with product catalog

NOTE: This implementation uses placeholder AI models.
In production, replace with fine-tuned computer vision models:
- Vision Transformer (ViT) for category classification
- CLIP for brand and visual similarity
- Custom embeddings for product matching
"""

from typing import Dict, List, Optional, Tuple
from PIL import Image
import json
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from models import ProductCatalog, ImageUpload, DeviceFingerprint
from image_processor import ImageProcessor


class ProductRecognitionService:
    """Service for recognizing products from uploaded images."""

    def __init__(self, db: Session):
        """
        Initialize recognition service.

        Args:
            db: Database session
        """
        self.db = db
        self.image_processor = ImageProcessor()

    def recognize_product(
        self,
        image_path: str,
        user_id: Optional[int] = None,
        include_prices: bool = True,
        consent_to_fingerprinting: bool = False
    ) -> Dict:
        """
        Main recognition pipeline - identify product from image.

        Args:
            image_path: Path to uploaded image
            user_id: Optional user ID if authenticated
            include_prices: Whether to fetch pricing data
            consent_to_fingerprinting: User consent for device tracking

        Returns:
            Dictionary with recognition results
        """
        start_time = datetime.now()

        # Step 1: Validate image
        is_valid, error_message = self.image_processor.validate_image(image_path)
        if not is_valid:
            return {
                "success": False,
                "error": error_message
            }

        # Step 2: Extract metadata
        metadata = self.image_processor.extract_exif(image_path)

        # Step 3: Create device fingerprint (if consented)
        device_id = None
        if consent_to_fingerprinting:
            device_id = self._track_device(image_path, metadata, user_id)

        # Step 4: Check for duplicate image (avoid re-processing)
        image_hash = self.image_processor.create_image_hash(image_path)
        existing_result = self._check_duplicate(image_hash)
        if existing_result:
            return existing_result

        # Step 5: Preprocess image for recognition
        processed_path = self.image_processor.preprocess_for_recognition(image_path)

        # Step 6: Detect category
        category_result = self._detect_category(processed_path)

        # Step 7: Recognize brand
        brand_result = self._recognize_brand(processed_path, category_result)

        # Step 8: Match specific product model
        product_matches = self._match_product(
            processed_path,
            category_result,
            brand_result
        )

        # Step 9: Get pricing data (if requested)
        if include_prices and product_matches:
            for match in product_matches:
                match["prices"] = self._get_product_prices(match["product_id"])

        # Step 10: Store upload record
        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        self._store_upload_record(
            image_path=image_path,
            image_hash=image_hash,
            device_id=device_id,
            user_id=user_id,
            metadata=metadata,
            results=product_matches,
            processing_time_ms=processing_time_ms
        )

        return {
            "success": True,
            "category": category_result,
            "brand": brand_result,
            "matches": product_matches,
            "metadata": {
                "camera": f"{metadata.get('camera_make', 'Unknown')} {metadata.get('camera_model', '')}".strip(),
                "upload_location": metadata.get("gps_info"),
                "processing_time_ms": processing_time_ms
            }
        }

    def _detect_category(self, image_path: str) -> Dict:
        """
        Detect product category from image.

        TODO: Replace with fine-tuned Vision Transformer (ViT) model.

        Args:
            image_path: Path to preprocessed image

        Returns:
            Category detection result
        """
        # PLACEHOLDER: In production, use fine-tuned ViT model
        # Example using transformers:
        # from transformers import ViTForImageClassification, ViTImageProcessor
        # model = ViTForImageClassification.from_pretrained("./models/category_classifier")
        # processor = ViTImageProcessor.from_pretrained("./models/category_classifier")
        # inputs = processor(images=Image.open(image_path), return_tensors="pt")
        # outputs = model(**inputs)
        # predicted_class = outputs.logits.argmax(-1).item()

        # Mock response for development
        categories = ["boots", "hats", "vests", "belts", "jeans"]
        confidence_scores = [0.85, 0.10, 0.03, 0.01, 0.01]

        return {
            "category": categories[0],  # Top prediction
            "confidence": confidence_scores[0],
            "all_predictions": [
                {"category": cat, "confidence": conf}
                for cat, conf in zip(categories, confidence_scores)
            ]
        }

    def _recognize_brand(self, image_path: str, category_result: Dict) -> Dict:
        """
        Recognize product brand from image.

        TODO: Replace with CLIP-based brand recognition.

        Args:
            image_path: Path to preprocessed image
            category_result: Category detection result

        Returns:
            Brand recognition result
        """
        # PLACEHOLDER: In production, use CLIP model
        # Example using CLIP:
        # import clip
        # model, preprocess = clip.load("ViT-B/32")
        # image = preprocess(Image.open(image_path)).unsqueeze(0)
        # brands = ["Ariat", "Stetson", "Justin Boots", "Wrangler", "Cinch"]
        # text = clip.tokenize([f"a photo of {brand} {category}" for brand in brands])
        # with torch.no_grad():
        #     image_features = model.encode_image(image)
        #     text_features = model.encode_text(text)
        #     similarity = (image_features @ text_features.T).softmax(dim=-1)

        category = category_result["category"]

        # Mock brand recognition based on category
        brand_database = {
            "boots": ["Ariat", "Justin Boots", "Lucchese", "Tony Lama"],
            "hats": ["Stetson", "Resistol", "American Hat Company", "Greeley Hat Works"],
            "vests": ["Outback Trading", "Scully", "Wyoming Traders", "Powder River"]
        }

        brands = brand_database.get(category, ["Unknown"])
        confidence_scores = [0.78, 0.12, 0.06, 0.04][:len(brands)]

        return {
            "brand": brands[0],
            "confidence": confidence_scores[0],
            "all_predictions": [
                {"brand": brand, "confidence": conf}
                for brand, conf in zip(brands, confidence_scores)
            ]
        }

    def _match_product(
        self,
        image_path: str,
        category_result: Dict,
        brand_result: Dict
    ) -> List[Dict]:
        """
        Match specific product model via visual similarity search.

        TODO: Replace with vector similarity search using pgvector.

        Args:
            image_path: Path to preprocessed image
            category_result: Category detection result
            brand_result: Brand recognition result

        Returns:
            List of product matches with similarity scores
        """
        # PLACEHOLDER: In production, use visual embeddings + pgvector
        # 1. Generate image embedding using CLIP or similar
        # 2. Query ProductCatalog with vector similarity search
        # 3. Filter by detected category and brand
        # 4. Return top N matches sorted by similarity

        category = category_result["category"]
        brand = brand_result["brand"]

        # Query database for products matching category and brand
        products = self.db.query(ProductCatalog).filter(
            ProductCatalog.category == category,
            ProductCatalog.brand == brand
        ).limit(5).all()

        # Mock similarity scores for now
        matches = []
        for i, product in enumerate(products):
            similarity_score = 0.92 - (i * 0.08)  # Mock decreasing scores

            matches.append({
                "product_id": product.id,
                "brand": product.brand,
                "model": product.model,
                "category": product.category,
                "description": product.description,
                "similarity_score": similarity_score,
                "image_urls": json.loads(product.image_urls) if product.image_urls else [],
                "msrp": product.msrp,
                "current_best_price": product.current_best_price
            })

        # If no products in database, return mock result
        if not matches:
            matches = [{
                "product_id": None,
                "brand": brand,
                "model": "Unknown Model",
                "category": category,
                "description": f"Product recognition found a {brand} {category}, but exact model not in catalog yet.",
                "similarity_score": 0.75,
                "image_urls": [],
                "msrp": None,
                "current_best_price": None,
                "note": "This is a mock result. Add products to the catalog for real matching."
            }]

        return matches

    def _get_product_prices(self, product_id: int) -> List[Dict]:
        """
        Get current pricing data for a product.

        Args:
            product_id: Product catalog ID

        Returns:
            List of prices from different stores
        """
        # TODO: Integrate with affiliate APIs or price database
        # For now, return mock prices

        if product_id is None:
            return []

        # Mock pricing data
        stores = ["Boot Barn", "Sheplers", "Cavender's", "Amazon"]
        base_price = 149.99

        prices = []
        for i, store in enumerate(stores):
            price = base_price + (i * 10)
            is_on_sale = i == 0  # First store has sale

            prices.append({
                "store_name": store,
                "price": price * 0.85 if is_on_sale else price,
                "original_price": price if is_on_sale else None,
                "is_on_sale": is_on_sale,
                "in_stock": True,
                "store_url": f"https://{store.lower().replace(' ', '')}.com",
                "last_updated": datetime.now().isoformat()
            })

        return sorted(prices, key=lambda x: x["price"])

    def _track_device(
        self,
        image_path: str,
        metadata: Dict,
        user_id: Optional[int]
    ) -> str:
        """
        Track device fingerprint from image metadata.

        Args:
            image_path: Path to image
            metadata: Extracted EXIF metadata
            user_id: Optional user ID

        Returns:
            Device ID (fingerprint hash)
        """
        device_id = self.image_processor.create_device_fingerprint(image_path, metadata)

        # Check if device exists
        device = self.db.query(DeviceFingerprint).filter(
            DeviceFingerprint.device_id == device_id
        ).first()

        if device:
            # Update existing device
            device.last_seen = datetime.now()
            device.upload_count += 1
            if user_id and not device.user_id:
                device.user_id = user_id  # Associate with user
        else:
            # Create new device fingerprint
            device = DeviceFingerprint(
                device_id=device_id,
                camera_make=metadata.get("camera_make"),
                camera_model=metadata.get("camera_model"),
                software=metadata.get("software"),
                user_id=user_id,
                metadata=json.dumps(metadata)
            )
            self.db.add(device)

        self.db.commit()
        return device_id

    def _check_duplicate(self, image_hash: str) -> Optional[Dict]:
        """
        Check if image was already processed (duplicate detection).

        Args:
            image_hash: Perceptual hash of image

        Returns:
            Cached result if duplicate found, None otherwise
        """
        # Query recent uploads with same hash (within last 24 hours)
        from datetime import timedelta

        recent_upload = self.db.query(ImageUpload).filter(
            ImageUpload.image_hash == image_hash,
            ImageUpload.upload_timestamp >= datetime.now() - timedelta(hours=24)
        ).first()

        if recent_upload and recent_upload.recognition_results:
            # Return cached result
            return {
                "success": True,
                "cached": True,
                "results": json.loads(recent_upload.recognition_results)
            }

        return None

    def _store_upload_record(
        self,
        image_path: str,
        image_hash: str,
        device_id: Optional[str],
        user_id: Optional[int],
        metadata: Dict,
        results: List[Dict],
        processing_time_ms: int
    ):
        """
        Store upload record in database for analytics.

        Args:
            image_path: Path to uploaded image
            image_hash: Perceptual hash
            device_id: Device fingerprint
            user_id: Optional user ID
            metadata: Image metadata
            results: Recognition results
            processing_time_ms: Processing time
        """
        # Extract GPS if available
        latitude = None
        longitude = None
        gps_info = metadata.get("gps_info")
        if gps_info and gps_info.get("available"):
            # TODO: Parse GPS coordinates from raw data
            pass

        upload = ImageUpload(
            user_id=user_id,
            device_id=device_id,
            image_hash=image_hash,
            file_path=image_path,
            exif_data=json.dumps(metadata),
            latitude=latitude,
            longitude=longitude,
            recognition_results=json.dumps(results),
            processing_time_ms=processing_time_ms
        )

        self.db.add(upload)
        self.db.commit()

    def get_upload_analytics(self, user_id: Optional[int] = None) -> Dict:
        """
        Get analytics on image uploads.

        Args:
            user_id: Optional user ID to filter analytics

        Returns:
            Analytics summary
        """
        query = self.db.query(ImageUpload)
        if user_id:
            query = query.filter(ImageUpload.user_id == user_id)

        total_uploads = query.count()

        # Get most recognized categories
        # TODO: Aggregate from recognition_results JSON

        # Get most popular brands
        # TODO: Aggregate from recognition_results JSON

        return {
            "total_uploads": total_uploads,
            "unique_devices": self.db.query(DeviceFingerprint).count(),
            "average_processing_time_ms": 1250,  # Mock for now
            "most_recognized_category": "boots",
            "most_recognized_brand": "Ariat"
        }
