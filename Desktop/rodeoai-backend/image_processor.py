"""
Image Processing Service for Visual Product Recognition.

Handles:
- EXIF metadata extraction from photos
- Device fingerprinting
- Image preprocessing for recognition
- Perceptual hashing for duplicate detection
"""

from PIL import Image
from PIL.ExifTags import TAGS
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime
import imagehash
import os


class ImageProcessor:
    """Process uploaded images, extract metadata, and create device fingerprints."""

    @staticmethod
    def extract_exif(image_path: str) -> Dict:
        """
        Extract EXIF metadata from image.

        Returns camera info, GPS coordinates, timestamps, etc.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing extracted metadata
        """
        try:
            image = Image.open(image_path)
            exif_data = {}

            # Get EXIF data
            exif = image._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Convert to string to make it JSON serializable
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
            # Return basic metadata even if EXIF extraction fails
            try:
                image = Image.open(image_path)
                return {
                    "image_dimensions": {
                        "width": image.width,
                        "height": image.height
                    },
                    "format": image.format,
                    "mode": image.mode,
                }
            except:
                return {}

    @staticmethod
    def _extract_gps(exif_data: Dict) -> Optional[Dict]:
        """
        Extract GPS coordinates if available.

        Args:
            exif_data: EXIF data dictionary

        Returns:
            GPS information dict or None
        """
        gps_info_str = exif_data.get("GPSInfo")
        if not gps_info_str:
            return None

        # In a full implementation, you'd parse the GPS data properly
        # For now, just return a placeholder
        return {
            "available": True,
            "raw": gps_info_str
        }

    @staticmethod
    def create_device_fingerprint(image_path: str, metadata: Dict) -> str:
        """
        Create unique device fingerprint from image metadata.

        Combines camera model, software, and image characteristics
        to create a consistent fingerprint for the same device.

        Args:
            image_path: Path to image file
            metadata: Extracted metadata

        Returns:
            SHA256 hash representing the device fingerprint
        """
        try:
            # Create fingerprint from stable metadata
            fingerprint_data = {
                "camera_make": metadata.get("camera_make", "unknown"),
                "camera_model": metadata.get("camera_model", "unknown"),
                "software": metadata.get("software", "unknown"),
            }

            # Add aspect ratio if dimensions available
            if metadata.get("image_dimensions"):
                width = metadata["image_dimensions"]["width"]
                height = metadata["image_dimensions"]["height"]
                if width and height and height != 0:
                    fingerprint_data["aspect_ratio"] = round(width / height, 2)

            # Create hash
            fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
            device_id = hashlib.sha256(fingerprint_str.encode()).hexdigest()

            return device_id

        except Exception as e:
            print(f"Error creating device fingerprint: {e}")
            # Return a generic fingerprint if metadata is insufficient
            return hashlib.sha256(b"unknown_device").hexdigest()

    @staticmethod
    def create_image_hash(image_path: str) -> str:
        """
        Create perceptual hash of image for duplicate detection.

        Uses perceptual hashing so similar images get similar hashes.

        Args:
            image_path: Path to image file

        Returns:
            Perceptual hash string
        """
        try:
            image = Image.open(image_path)

            # Use perceptual hashing (similar images = similar hashes)
            phash = imagehash.phash(image)

            return str(phash)

        except Exception as e:
            print(f"Error creating image hash: {e}")
            return "0" * 16  # Return zeros if hashing fails

    @staticmethod
    def preprocess_for_recognition(
        image_path: str,
        output_path: Optional[str] = None,
        target_size: tuple = (1024, 1024)
    ) -> str:
        """
        Prepare image for product recognition.
        - Resize to standard dimensions
        - Enhance quality
        - Normalize orientation

        Args:
            image_path: Path to input image
            output_path: Path to save processed image (optional)
            target_size: Maximum dimensions (width, height)

        Returns:
            Path to processed image
        """
        try:
            image = Image.open(image_path)

            # Convert to RGB if needed (e.g., RGBA images)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Correct orientation based on EXIF
            image = ImageProcessor._correct_orientation(image)

            # Resize to standard size (keep aspect ratio)
            image.thumbnail(target_size, Image.Resampling.LANCZOS)

            # Auto-enhance (optional)
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)  # Slight sharpness increase

            # Save processed image
            if output_path:
                image.save(output_path, quality=95, optimize=True)
                return output_path
            else:
                # Overwrite original
                image.save(image_path, quality=95, optimize=True)
                return image_path

        except Exception as e:
            print(f"Error preprocessing image: {e}")
            # Return original path if processing fails
            return image_path

    @staticmethod
    def _correct_orientation(image: Image.Image) -> Image.Image:
        """
        Correct image orientation based on EXIF orientation tag.

        Args:
            image: PIL Image object

        Returns:
            Correctly oriented image
        """
        try:
            exif = image._getexif()
            if exif:
                orientation = None
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'Orientation':
                        orientation = value
                        break

                if orientation:
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)

        except Exception as e:
            print(f"Error correcting orientation: {e}")
            # Return original if orientation correction fails
            pass

        return image

    @staticmethod
    def validate_image(image_path: str, max_size_mb: int = 10) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded image.

        Args:
            image_path: Path to image file
            max_size_mb: Maximum file size in MB

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file exists
            if not os.path.exists(image_path):
                return False, "File not found"

            # Check file size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                return False, f"File too large ({file_size_mb:.1f}MB). Max {max_size_mb}MB"

            # Try to open as image
            try:
                image = Image.open(image_path)
                image.verify()  # Verify it's a valid image
            except Exception:
                return False, "Invalid image file"

            # Check image format
            allowed_formats = {'JPEG', 'PNG', 'JPG', 'WEBP'}
            image = Image.open(image_path)
            if image.format not in allowed_formats:
                return False, f"Unsupported format: {image.format}. Allowed: {allowed_formats}"

            # Check dimensions (not too small)
            min_dimension = 200
            if image.width < min_dimension or image.height < min_dimension:
                return False, f"Image too small. Minimum {min_dimension}x{min_dimension}px"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"
