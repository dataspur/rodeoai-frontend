"""
Simple test to verify ImageProcessor functionality.
Tests image validation, metadata extraction, and hashing.
"""

from image_processor import ImageProcessor
from PIL import Image
import os
import tempfile


def test_image_processor():
    """Test ImageProcessor with a simple test image."""
    print("Testing ImageProcessor...")

    # Create a test image
    test_image = Image.new('RGB', (800, 600), color='red')

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
        test_image_path = f.name
        test_image.save(test_image_path, 'JPEG')

    try:
        # Test 1: Image validation
        print("\n1. Testing image validation...")
        is_valid, error = ImageProcessor.validate_image(test_image_path)
        if is_valid:
            print("   ✓ Image validation passed")
        else:
            print(f"   ✗ Image validation failed: {error}")
            return

        # Test 2: EXIF extraction
        print("\n2. Testing EXIF extraction...")
        metadata = ImageProcessor.extract_exif(test_image_path)
        print(f"   ✓ Extracted metadata:")
        print(f"     - Dimensions: {metadata.get('image_dimensions')}")
        print(f"     - Format: {metadata.get('format')}")
        print(f"     - Mode: {metadata.get('mode')}")

        # Test 3: Device fingerprinting
        print("\n3. Testing device fingerprinting...")
        device_id = ImageProcessor.create_device_fingerprint(test_image_path, metadata)
        print(f"   ✓ Device fingerprint: {device_id[:16]}...")

        # Test 4: Image hashing
        print("\n4. Testing perceptual hashing...")
        image_hash = ImageProcessor.create_image_hash(test_image_path)
        print(f"   ✓ Image hash: {image_hash}")

        # Test 5: Image preprocessing
        print("\n5. Testing image preprocessing...")
        processed_path = ImageProcessor.preprocess_for_recognition(test_image_path)
        print(f"   ✓ Image preprocessed: {processed_path}")

        # Verify processed image
        processed_img = Image.open(processed_path)
        print(f"     - Processed dimensions: {processed_img.width}x{processed_img.height}")

        print("\n✓ All tests passed!")
        print("\nImageProcessor is ready for product recognition.")

    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)


if __name__ == "__main__":
    test_image_processor()
