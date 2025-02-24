"""
Centralized format definitions for the HungerRush Image Processing Application.
All image format configurations are defined here to avoid duplication.
"""
from typing import Dict, Tuple, Any

# Format specifications with all required information
FORMAT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "APPICON": {
        "size": (1024, 1024),
        "bg_color": (0, 0, 0, 0),  # Transparent
        "quality": 95,
        "optimize": True,
        "description": "Application icon with optional transparency"
    },
    "DEFAULT": {
        "size": (1242, 1902),
        "bg_color": (255, 255, 255, 255),  # White background
        "quality": 95,
        "optimize": True,
        "description": "Standard splash screen with maintained aspect ratio"
    },
    "DEFAULT_LG": {
        "size": (1242, 2208),
        "bg_color": (255, 255, 255, 255),  # White background
        "quality": 95,
        "optimize": True,
        "description": "Large splash screen for higher resolution devices"
    },
    "DEFAULT_XL": {
        "size": (1242, 2688),
        "bg_color": (255, 255, 255, 255),  # White background
        "quality": 95,
        "optimize": True,
        "description": "Extra large splash screen for modern devices"
    },
    "FEATURE_GRAPHIC": {
        "size": (1024, 500),
        "bg_color": (255, 255, 255, 255),  # White background
        "quality": 95,
        "optimize": True,
        "description": "Feature graphic banner for store listings"
    },
    "LOGO": {
        "size": (1024, 1024),
        "bg_color": (0, 0, 0, 0),  # Transparent
        "quality": 95,
        "optimize": True,
        "description": "High-resolution square logo with transparency"
    },
    "LOGO_WIDE": {
        "size": (1024, 500),
        "bg_color": (0, 0, 0, 0),  # Transparent
        "quality": 95,
        "optimize": True,
        "description": "High-resolution wide logo with transparency"
    },
    "PUSH": {
        "size": (96, 96),
        "bg_color": (255, 255, 255, 0),  # White with transparency
        "quality": 95,
        "optimize": True,
        "description": "Small notification icon (white with transparency)"
    }
}

# Common image processing settings
IMAGE_SETTINGS = {
    "quality": 95,
    "optimize": True,
    "format": "PNG",
    "min_dimension": 90,
    "max_dimension": 5000,
    "max_file_size": 50 * 1024 * 1024  # 50MB
}

# Allowed image formats
ALLOWED_FORMATS = {
    ".png", ".jpg", ".jpeg",
    ".gif", ".bmp", ".tiff", ".jfif"
}

# Error messages for image validation
ERROR_MESSAGES = {
    "invalid_image": "The selected file is not a valid image format.",
    "file_too_large": f"File exceeds the maximum allowed size of {IMAGE_SETTINGS['max_file_size'] // (1024 * 1024)}MB.",
    "resolution_too_low": f"Image dimensions must be at least {IMAGE_SETTINGS['min_dimension']}x{IMAGE_SETTINGS['min_dimension']}px.",
    "resolution_too_high": f"Image dimensions cannot exceed {IMAGE_SETTINGS['max_dimension']}x{IMAGE_SETTINGS['max_dimension']}px."
}