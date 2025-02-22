"""
Base settings and configuration for image processing.
"""

from pathlib import Path
from typing import Dict, Tuple, Set
import logging

class BaseImageProcessor:
    """Shared configuration and validation for image processors."""

    # Format specifications
    FORMAT_CONFIGS = {
        "APPICON": {
            "size": (1024, 1024),
            "bg_color": (0, 0, 0, 0),  # Transparent
            "quality": 95,
            "optimize": True
        },
        "DEFAULT": {
            "size": (1242, 1902),
            "bg_color": (255, 255, 255, 255),  # White background
            "quality": 95,
            "optimize": True
        },
        "DEFAULT_LG": {
            "size": (1242, 2208),
            "bg_color": (255, 255, 255, 255),
            "quality": 95,
            "optimize": True
        },
        "DEFAULT_XL": {
            "size": (1242, 2688),
            "bg_color": (255, 255, 255, 255),
            "quality": 95,
            "optimize": True
        },
        "FEATURE_GRAPHIC": {
            "size": (1024, 500),
            "bg_color": (255, 255, 255, 255),
            "quality": 95,
            "optimize": True
        },
        "LOGO": {
            "size": (1024, 1024),
            "bg_color": (0, 0, 0, 0),  # Transparent
            "quality": 95,
            "optimize": True
        },
        "PUSH": {
            "size": (96, 96),
            "bg_color": (255, 255, 255, 0),  # White with transparency
            "quality": 95,
            "optimize": True
        }
    }

    # Common settings
    QUALITY: int = 95
    OPTIMIZE: bool = True
    MIN_DIMENSION: int = 90
    MAX_DIMENSION: int = 5000
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Allowed formats
    ALLOWED_FORMATS: Set[str] = {
        ".png", ".jpg", ".jpeg",
        ".gif", ".bmp", ".tiff", ".jfif"
    }

    # Error messages
    ERROR_MESSAGES = {
        "invalid_image": "The selected file is not a valid image format.",
        "file_too_large": f"File exceeds the maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB.",
        "resolution_too_low": f"Image dimensions must be at least {MIN_DIMENSION}x{MIN_DIMENSION}px.",
        "resolution_too_high": f"Image dimensions cannot exceed {MAX_DIMENSION}x{MAX_DIMENSION}px."
    }

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
    def get_format_config(cls, format_name: str) -> Dict:
        """
        Get configuration for a specific format.
        
        Args:
            format_name (str): Name of the format (e.g., "APPICON")
            
        Returns:
            Dict: Format configuration including size, background color, etc.
        """
        return cls.FORMAT_CONFIGS[format_name]