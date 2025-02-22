import pytest
import shutil
from src.utils.logging import get_logger

# Initialize test logger
logger = get_logger(__name__)

@pytest.fixture(scope="function")
def temp_test_dir(tmp_path):
    """
    Creates a temporary directory for test-generated files.
    Cleans up automatically after each test function.
    """
    test_dir = tmp_path / "test_output"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
    shutil.rmtree(test_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def sample_image(temp_test_dir):
    """
    Creates a sample test image for image processing tests.
    """
    from PIL import Image

    img_path = temp_test_dir / "test_image.png"
    img = Image.new("RGBA", (200, 200), (255, 0, 0, 255))  # Red square
    img.save(img_path)
    return img_path

@pytest.fixture(scope="function")
def sample_invalid_image(temp_test_dir):
    """
    Creates an invalid/corrupt test image file.
    """
    img_path = temp_test_dir / "invalid_image.png"
    with open(img_path, "wb") as f:
        f.write(b"not an image")
    return img_path

@pytest.fixture(scope="session")
def log_test_results():
    """
    Logs test failures for debugging.
    """
    logger.info("Starting test session.")
    yield
    logger.info("Test session complete.")