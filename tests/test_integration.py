import pytest
from PIL import Image
from pathlib import Path
from src.services.image_processing_service import ImageProcessingService
from src.core.error_handler import ImageProcessingError

@pytest.fixture(scope="function")
def image_service():
    """Provides an instance of ImageProcessingService for integration tests."""
    return ImageProcessingService()

@pytest.fixture(scope="function")
def temp_output_dir(tmp_path):
    """Creates a temporary directory for processed images."""
    output_dir = tmp_path / "processed_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture(scope="function")
def sample_image(tmp_path):
    """Creates a sample test image."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGBA", (500, 500), (255, 0, 0, 255))  # Red image
    img.save(img_path)
    return img_path

@pytest.fixture(scope="function")
def corrupt_image(tmp_path):
    """Creates a corrupt test image file."""
    corrupt_img_path = tmp_path / "corrupt_image.png"
    with open(corrupt_img_path, "wb") as f:
        f.write(b"this is not an image file")
    return corrupt_img_path

def test_full_image_processing_pipeline(image_service, sample_image, temp_output_dir):
    """Tests the full image processing pipeline end-to-end."""
    formats = {"DEFAULT"}  # Test with DEFAULT format

    results = image_service.process_batch([sample_image], temp_output_dir, formats)

    assert len(results["successful"]) == 1, "Should successfully process one image"
    assert len(results["failed"]) == 0, "Should have no failed processes"

    output_path = results["successful"][0]
    assert output_path.exists(), "Processed image should exist"

    # Verify output matches expected dimensions
    with Image.open(output_path) as img:
        assert img.size == (1242, 1902), "Image should be resized to DEFAULT format dimensions"

def test_integration_invalid_image(image_service, corrupt_image, temp_output_dir):
    """Tests integration with a corrupt image file."""
    formats = {"DEFAULT"}

    results = image_service.process_batch([corrupt_image], temp_output_dir, formats)

    assert len(results["successful"]) == 0, "Should have no successful processes"
    assert len(results["failed"]) == 1, "Should have one failed process"

def test_multiple_format_generation(image_service, sample_image, temp_output_dir):
    """Tests generating multiple output formats."""
    formats = {"APPICON", "DEFAULT", "LOGO"}

    results = image_service.process_batch([sample_image], temp_output_dir, formats)

    assert len(results["successful"]) == len(formats), "Should process all formats"
    assert len(results["failed"]) == 0, "Should have no failed processes"

    # Verify each format's output
    expected_sizes = {
        "APPICON": (1024, 1024),
        "DEFAULT": (1242, 1902),
        "LOGO": (1024, 1024)
    }

    for output_path in results["successful"]:
        format_name = output_path.stem.split("_")[-1]
        assert output_path.exists(), f"{format_name} should be generated"
        with Image.open(output_path) as img:
            assert img.size == expected_sizes[format_name], f"{format_name} should have correct size"

def test_push_notification_creation(image_service, sample_image, temp_output_dir):
    """Tests push notification icon generation."""
    formats = {"PUSH"}

    results = image_service.process_batch([sample_image], temp_output_dir, formats)

    assert len(results["successful"]) == 1, "Should successfully process push notification"
    assert len(results["failed"]) == 0, "Should have no failed processes"

    output_path = results["successful"][0]
    assert output_path.exists(), "Push notification image should be created"

    with Image.open(output_path) as img:
        assert img.size == (96, 96), "Push image should be 96x96"