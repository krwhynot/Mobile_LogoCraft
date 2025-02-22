"""
Image processing functionality for the HungerRush Image Processor.
"""
from PIL import Image
from pathlib import Path
import logging
from .base import BaseImageProcessor

logger = logging.getLogger(__name__)

class ImageProcessor(BaseImageProcessor):
    """Handles image processing operations."""
    
    def process_image(self, input_path: Path, output_path: Path, width: int, height: int, bg_color: tuple = (0, 0, 0, 0)):
        """
        Process an image to the specified dimensions.
        
        Args:
            input_path (Path): Path to input image
            output_path (Path): Path to save output image
            width (int): Target width in pixels
            height (int): Target height in pixels
            bg_color (tuple): Background color in RGBA format
        """
        try:
            # Validate input before processing
            self.validate_input(input_path, output_path)
            
            with Image.open(input_path) as img:
                # Convert to RGBA for consistent handling
                img = img.convert("RGBA")
                
                # Calculate scaling to maintain aspect ratio
                img_ratio = img.width / img.height
                target_ratio = width / height
                
                if img_ratio > target_ratio:
                    # Image is wider than target
                    new_width = int(height * img_ratio)
                    new_height = height
                else:
                    # Image is taller than target
                    new_width = width
                    new_height = int(width / img_ratio)
                
                # Resize with high quality
                resized = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Create new image with target dimensions
                final = Image.new("RGBA", (width, height), bg_color)
                
                # Calculate centering offset
                left = (width - new_width) // 2
                top = (height - new_height) // 2
                
                # Paste resized image
                final.paste(resized, (left, top))
                
                # Save with optimization
                final.save(output_path, "PNG", 
                         optimize=self.OPTIMIZE,
                         quality=self.QUALITY)
                logger.info(f"Successfully processed image to {width}x{height}: {output_path}")
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

    def process_format(self, input_path: Path, output_path: Path, format_name: str):
        """
        Process an image according to a predefined format.
        
        Args:
            input_path (Path): Source image path
            output_path (Path): Output image path
            format_name (str): Name of the format to apply
        """
        config = self.get_format_config(format_name)
        self.process_image(
            input_path,
            output_path,
            width=config["size"][0],
            height=config["size"][1],
            bg_color=config["bg_color"]
        )