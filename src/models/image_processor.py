"""
Image processing functionality for the HungerRush Image Processor.
"""
from PIL import Image
from pathlib import Path
import logging
from .base import BaseImageProcessor
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# 1. File Validation Settings
FILE_VALIDATION = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB max size
    'allowed_formats': {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".jfif"},
    'chunk_size': 1024 * 1024  # File reading buffer
}

# 2. Dimension Settings
DIMENSION_VALIDATION = {
    'min_dimension': 90,
    'max_dimension': 5000
}

# 3. Format Definitions
FORMAT_CONFIGS = {
    'APPICON': {
        'size': (1024, 1024),
        'bg_color': (0, 0, 0, 0),  # Transparent
        'description': 'Application icon with optional transparency'
    },
    'DEFAULT': {
        'size': (1242, 1902),
        'bg_color': (255, 255, 255, 255),  # White background
        'description': 'Splash screen with maintained aspect ratio'
    },
    'DEFAULT_LG': {
        'size': (1242, 2208),
        'bg_color': (255, 255, 255, 255),  # White background
        'description': 'Large splash screen'
    },
    'DEFAULT_XL': {
        'size': (1242, 2688),
        'bg_color': (255, 255, 255, 255),  # White background
        'description': 'Extra large splash screen'
    },
    'FEATURE_GRAPHIC': {
        'size': (1024, 500),
        'bg_color': (255, 255, 255, 255),  # White background
        'description': 'Feature graphic with solid background'
    },
    'LOGO': {
        'size': (1024, 1024),
        'bg_color': (0, 0, 0, 0),  # Transparent
        'description': 'High-resolution logo with transparency'
    },
    'LOGO_WIDE': {
        'size': (1024, 500),
        'bg_color': (0, 0, 0, 0),  # Transparent
        'description': 'Wide high-resolution logo with transparency'
    }
}

# 4. Processing Settings
PROCESSING_SETTINGS = {
    'target_mode': 'RGBA',
    'resampling_large': Image.LANCZOS,
    'resampling_small': Image.BOX,
    'progressive_threshold': 0.5,
    'progressive_factor': 0.707  # sqrt(0.5)
}

# 5. Save Settings
SAVE_SETTINGS = {
    'format': 'PNG',
    'optimize': True,
    'quality': 95,
    'compress_level': 6
}

class ImageProcessor(BaseImageProcessor):
    """Handles image processing operations."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)
        self.formats = FORMAT_CONFIGS

    def get_format_config(self, format_name: str) -> dict:
        """
        Get format configuration.
        Overrides base class method to use local format definitions.
        """
        if format_name not in self.formats:
            raise ValueError(f"Unknown format: {format_name}")
        return self.formats[format_name]

    def validate_file(self, file_path: Path) -> bool:
        """Validate file existence, format and size."""
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in FILE_VALIDATION['allowed_formats']:
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        if file_path.stat().st_size > FILE_VALIDATION['max_file_size']:
            raise ValueError(f"File too large: {file_path.stat().st_size / (1024 * 1024):.1f}MB")

        return True

    def validate_dimensions(self, image: Image.Image) -> bool:
        """Validate image dimensions."""
        width, height = image.size
        if width < DIMENSION_VALIDATION['min_dimension'] or height < DIMENSION_VALIDATION['min_dimension']:
            raise ValueError(f"Image too small: {width}x{height}")

        if width > DIMENSION_VALIDATION['max_dimension'] or height > DIMENSION_VALIDATION['max_dimension']:
            raise ValueError(f"Image too large: {width}x{height}")

        return True

    def calculate_dimensions(self, img_size: Tuple[int, int], target_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate new dimensions maintaining aspect ratio."""
        img_width, img_height = img_size
        target_width, target_height = target_size

        img_ratio = img_width / img_height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            new_width = int(target_height * img_ratio)
            new_height = target_height
        else:
            new_width = target_width
            new_height = int(target_width / img_ratio)

        return (new_width, new_height)

    def process_image(self, input_path: Path, output_path: Path, width: int, height: int, bg_color: tuple = (0, 0, 0, 0)):
        """
        Process an image to the specified dimensions.
        """
        try:
            self.validate_file(input_path)

            with Image.open(input_path) as img:
                self.validate_dimensions(img)
                img = img.convert(PROCESSING_SETTINGS['target_mode'])

                new_size = self.calculate_dimensions(img.size, (width, height))

                # Progressive downscaling if needed
                if (new_size[0] < img.width * PROCESSING_SETTINGS['progressive_threshold'] or
                    new_size[1] < img.height * PROCESSING_SETTINGS['progressive_threshold']):
                    intermediate_size = (
                        int(img.width * PROCESSING_SETTINGS['progressive_factor']),
                        int(img.height * PROCESSING_SETTINGS['progressive_factor'])
                    )
                    img = img.resize(intermediate_size, PROCESSING_SETTINGS['resampling_small'])

                resized = img.resize(new_size, PROCESSING_SETTINGS['resampling_large'])
                final = Image.new(PROCESSING_SETTINGS['target_mode'], (width, height), bg_color)

                # Center the image
                left = (width - new_size[0]) // 2
                top = (height - new_size[1]) // 2

                # Paste with alpha mask
                final.paste(resized, (left, top), resized)

                # Save with optimization
                final.save(
                    output_path,
                    SAVE_SETTINGS['format'],
                    optimize=SAVE_SETTINGS['optimize'],
                    quality=SAVE_SETTINGS['quality'],
                    compress_level=SAVE_SETTINGS['compress_level']
                )

                self.logger.info(f"Successfully processed image to {width}x{height}: {output_path}")

        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise

    def process_format(self, input_path: Path, output_path: Path, format_name: str):
        """
        Process an image according to a predefined format.
        """
        try:
            config = self.get_format_config(format_name)

            # Ensure correct output filename
            output_path = Path(output_path)
            output_path = output_path.parent / f"{format_name}.PNG"

            self.process_image(
                input_path,
                output_path,
                width=config["size"][0],
                height=config["size"][1],
                bg_color=config["bg_color"]
            )

            self.logger.info(f"Successfully processed image to format {format_name}")

        except Exception as e:
            self.logger.error(f"Error processing format {format_name}: {str(e)}")
            raise

    def process_logo(self, input_path: Path, output_path: Path, wide: bool = False):
        """
        Process an image as a logo, either square or wide format.
        """
        format_name = 'LOGO_WIDE' if wide else 'LOGO'
        self.process_format(input_path, output_path, format_name)
