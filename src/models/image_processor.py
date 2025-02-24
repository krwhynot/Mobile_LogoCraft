"""
Image processing functionality for the HungerRush Image Processor.
"""
from PIL import Image
from pathlib import Path
import logging
from .base import BaseImageProcessor
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Processing Settings
PROCESSING_SETTINGS = {
    'target_mode': 'RGBA',
    'resampling_large': Image.LANCZOS,
    'resampling_small': Image.BOX,
    'progressive_threshold': 0.5,
    'progressive_factor': 0.707  # sqrt(0.5)
}

# Save Settings
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

    def calculate_dimensions(self, img_size: Tuple[int, int], target_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Resize the image dynamically while maintaining aspect ratio.

        Returns:
            Tuple[int, int, int, int]: (new width, new height, left offset, top offset)
        """
        img_width, img_height = img_size
        target_width, target_height = target_size

        # Calculate aspect ratios
        img_ratio = img_width / img_height
        target_ratio = target_width / target_height

        # Scale image to fit within target size
        if img_ratio > target_ratio:
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * img_ratio)

        # Center the image
        left_offset = (target_width - new_width) // 2
        top_offset = (target_height - new_height) // 2

        return new_width, new_height, left_offset, top_offset

    def process_image(self, input_path: Path, output_path: Path, width: int, height: int, bg_color: tuple = (0, 0, 0, 0)):
        """
        Process an image to dynamically fit within the target canvas without distortion.
        """
        try:
            self.validate_input(input_path, output_path)

            with Image.open(input_path) as img:
                # Validate image dimensions
                if img.width < self.MIN_DIMENSION or img.height < self.MIN_DIMENSION:
                    raise ValueError(f"Image too small: {img.width}x{img.height}")
                if img.width > self.MAX_DIMENSION or img.height > self.MAX_DIMENSION:
                    raise ValueError(f"Image too large: {img.width}x{img.height}")
                    
                img = img.convert(PROCESSING_SETTINGS['target_mode'])

                # Get dynamically resized dimensions
                new_width, new_height, left, top = self.calculate_dimensions(img.size, (width, height))

                # Resize the image dynamically
                resized = img.resize((new_width, new_height), PROCESSING_SETTINGS['resampling_large'])

                # Create a blank canvas with the target size
                final = Image.new(PROCESSING_SETTINGS['target_mode'], (width, height), bg_color)

                # Paste the resized image onto the centered position in the canvas
                final.paste(resized, (left, top), resized if 'A' in img.getbands() else None)

                # Save the processed image
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
            raise  # Ensures the error is properly logged and re-raised

    def process_format(self, input_path: Path, output_path: Path, format_name: str):
        """Process an image according to a predefined format."""
        try:
            # Get format configuration from the central repository
            config = self.get_format_config(format_name)
            
            self.process_image(
                input_path,
                output_path,
                width=config["size"][0],
                height=config["size"][1],
                bg_color=config["bg_color"]
            )

            self.logger.info(f"Successfully processed image to format {format_name}: {output_path}")

        except Exception as e:
            self.logger.error(f"Error processing format {format_name}: {str(e)}")
            raise

    def process_logo(self, input_path: Path, output_path: Path, wide: bool = False):
        """
        Process an image as a logo, either square or wide format.
        
        Args:
            input_path: Path to the input image
            output_path: Path where the processed logo will be saved
            wide: If True, process as LOGO_WIDE, otherwise as LOGO
        """
        format_name = 'LOGO_WIDE' if wide else 'LOGO'
        self.logger.info(f"Processing logo as format: {format_name}")
        
        try:
            config = self.get_format_config(format_name)
            
            self.process_image(
                input_path,
                output_path,
                width=config["size"][0],
                height=config["size"][1],
                bg_color=config["bg_color"]
            )
            
            self.logger.info(f"Successfully processed {format_name}: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing {format_name}: {str(e)}")
            raise