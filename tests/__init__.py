"""Test package initialization."""
from pathlib import Path

# Set up test directory path
TEST_DIR = Path(__file__).parent
TEST_ASSETS_DIR = TEST_DIR / "assets"
DEBUG_OUTPUT_DIR = TEST_DIR / "debug_output"

# Create necessary directories
DEBUG_OUTPUT_DIR.mkdir(exist_ok=True)
