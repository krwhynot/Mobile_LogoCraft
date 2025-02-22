"""Tests for Push Notification Icon Processing Service."""
import pytest
from pathlib import Path
import numpy as np
from PIL import Image

from src.services.image_processing_service import ImageProcessingService
from src.core.error_handler import ImageProcessingError

# Define test directories
TEST_IMAGES_DIR = Path(__file__).parent / 'assets' / 'test_images'
OUTPUT_DIR = Path(__file__).parent / 'assets' / 'output' / 'push_icons'

@pytest.fixture(autouse=True)
def setup_output_dir():
    """Ensure output directory exists and is clean before each test."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Clean up existing files
    for file in OUTPUT_DIR.glob('*.png'):
        file.unlink()
    return OUTPUT_DIR

@pytest.fixture
def image_service():
    """Provides an instance of ImageProcessingService."""
    return ImageProcessingService()

def verify_push_icon(output_path):
    """Verify that the output icon meets Android requirements."""
    assert output_path.exists()

    # Verify output image
    with Image.open(output_path) as img:
        # Check dimensions
        assert img.size == (96, 96)
        # Check mode
        assert img.mode == 'RGBA'

        # Convert to numpy for detailed analysis
        img_array = np.array(img)

        # Check transparency
        alpha_channel = img_array[..., 3]
        assert np.any(alpha_channel == 0), "No transparent pixels found"
        assert np.any(alpha_channel == 255), "No opaque pixels found"

        # Check white foreground
        rgb = img_array[..., :3]
        white_pixels = np.all(rgb == [255, 255, 255], axis=2)
        assert np.any(white_pixels), "No white pixels found"

def test_process_all_test_images(image_service, setup_output_dir):
    """Process all images in the test directory."""
    # Get all PNG files
    test_images = sorted(TEST_IMAGES_DIR.glob('*.png'))
    assert len(test_images) > 0, "No test images found"

    formats = {"PUSH"}
    results = image_service.process_batch(test_images, setup_output_dir, formats)

    assert len(results["successful"]) == len(test_images), "All images should be processed successfully"
    assert len(results["failed"]) == 0, "No images should fail processing"

    # Verify each output
    for output_path in results["successful"]:
        verify_push_icon(output_path)

def test_nonexistent_file(image_service, setup_output_dir):
    """Test handling of nonexistent input file."""
    nonexistent_file = TEST_IMAGES_DIR / 'nonexistent.png'
    formats = {"PUSH"}

    results = image_service.process_batch([nonexistent_file], setup_output_dir, formats)

    assert len(results["successful"]) == 0, "Should not process nonexistent file"
    assert len(results["failed"]) == 1, "Should report failure for nonexistent file"

def test_small_image(image_service, setup_output_dir):
    """Test handling of images smaller than minimum size."""
    small_image_path = TEST_IMAGES_DIR / 'small_test.png'

    # Create a 32x32 test image
    img = Image.new('RGB', (32, 32), color='white')
    img.save(small_image_path)

    formats = {"PUSH"}
    results = image_service.process_batch([small_image_path], setup_output_dir, formats)

    assert len(results["successful"]) == 0, "Should not process image smaller than minimum size"
    assert len(results["failed"]) == 1, "Should report failure for small image"

    # Cleanup
    small_image_path.unlink(missing_ok=True)