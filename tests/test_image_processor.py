import pytest
from PIL import Image
from src.services.image_processing_service import ImageProcessingService
from src.core.error_handler import ImageProcessingError

@pytest.fixture(scope="function")
def image_service():
    """Provides an instance of ImageProcessingService for testing."""
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

def test_process_image_success(image_service, sample_image, temp_output_dir):
    """Tests successful image processing."""
    formats = {"DEFAULT"}  # Test with DEFAULT format (1242x1902)

    results = image_service.process_batch([sample_image], temp_output_dir, formats)

    assert len(results["successful"]) == 1, "Should successfully process one image"
    assert len(results["failed"]) == 0, "Should have no failed processes"

    output_path = results["successful"][0]
    assert output_path.exists(), "Processed image should exist"

    with Image.open(output_path) as img:
        assert img.size == (1242, 1902), "Image should be resized to DEFAULT format dimensions"

def test_process_image_invalid_format(image_service, corrupt_image, temp_output_dir):
    """Tests processing a corrupt image file."""
    formats = {"DEFAULT"}

    results = image_service.process_batch([corrupt_image], temp_output_dir, formats)

    assert len(results["successful"]) == 0, "Should have no successful processes"
    assert len(results["failed"]) == 1, "Should have one failed process"

def test_push_notification_creation(image_service, sample_image, temp_output_dir):
    """Tests push notification image creation."""
    formats = {"PUSH"}

    results = image_service.process_batch([sample_image], temp_output_dir, formats)

    assert len(results["successful"]) == 1, "Should successfully process push notification"
    assert len(results["failed"]) == 0, "Should have no failed processes"

    output_path = results["successful"][0]
    assert output_path.exists(), "Push notification image should be created"

    with Image.open(output_path) as img:
        assert img.size == (96, 96), "Push image should be 96x96"
