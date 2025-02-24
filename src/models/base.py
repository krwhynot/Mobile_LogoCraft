"""
Base settings and configuration for image processing.
"""

from pathlib import Path
from typing import Dict, Tuple, Set, Any
import logging

from src.config.formats import FORMAT_CONFIGS, IMAGE_SETTINGS, ALLOWED_FORMATS, ERROR_MESSAGES

class BaseImageProcessor:
    """Shared configuration and validation for image processors."""

    # Import format configurations from centralized config
    FORMAT_CONFIGS = FORMAT_CONFIGS

    # Common settings imported from centralized config
    QUALITY = IMAGE_SETTINGS["quality"]
    OPTIMIZE = IMAGE_SETTINGS["optimize"]
    MIN_DIMENSION = IMAGE_SETTINGS["min_dimension"]
    MAX_DIMENSION = IMAGE_SETTINGS["max_dimension"]
    MAX_FILE_SIZE = IMAGE_SETTINGS["max_file_size"]

    # Allowed formats imported from centralized config
    ALLOWED_FORMATS: Set[str] = ALLOWED_FORMATS

    # Error messages imported from centralized config
    ERROR_MESSAGES = ERROR_MESSAGES

    def __init__(self):
        """Initialize logger for image processing."""
        self.logger = logging.getLogger(__name__)

    @classmethod
    def validate_input(cls, input_path: Path, output_path: Path) -> None:
        """
        Validate input and output paths with comprehensive checks.
        
        Args:
            input_path (Path): Source image path
            output_path (Path): Destination image path
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file fails validation checks
        """
        if not input_path.is_file():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # File size check
        file_size = input_path.stat().st_size
        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError(cls.ERROR_MESSAGES["file_too_large"])

        # File extension check
        if input_path.suffix.lower() not in cls.ALLOWED_FORMATS:
            raise ValueError(cls.ERROR_MESSAGES["invalid_image"])

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_format_config(cls, format_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific format.
        
        Args:
            format_name (str): Name of the format (e.g., "APPICON")
            
        Returns:
            Dict: Format configuration including size, background color, etc.
        """
        return cls.FORMAT_CONFIGS[format_name]