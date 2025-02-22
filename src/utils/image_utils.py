from PIL import Image
from typing import Tuple, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Define constraints
MIN_DIMENSION = 90
MAX_DIMENSION = 5000
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for efficient memory handling

class ImageUtils:
    """Utility functions for image validation, resizing, and format handling."""

    @staticmethod
    def validate_image(img: Union[Image.Image, Path, str]) -> Tuple[bool, str]:
        """
        Validate image dimensions, format, and corruption checks.

        Args:
            img (Union[Image.Image, Path, str]): Image object or file path.

        Returns:
            Tuple[bool, str]: (Validation result, message)
        """
        try:
            if isinstance(img, (str, Path)):
                img = Image.open(img)

            if not isinstance(img, Image.Image):
                return False, "Invalid image object."

            try:
                img.verify()  # Check for corruption
            except Exception as e:
                return False, f"Corrupted image: {e}"

            if img.width < MIN_DIMENSION or img.height < MIN_DIMENSION:
                return False, f"Image too small: {img.width}x{img.height}"

            if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                return False, f"Image too large: {img.width}x{img.height}"

            return True, "Image validation successful."

        except Exception as e:
            return False, str(e)

    @staticmethod
    def optimal_downscale(img: Image.Image, target_size: Tuple[int, int], resampling=Image.LANCZOS) -> Image.Image:
        """
        Downscale an image while maintaining aspect ratio.

        Args:
            img (Image.Image): The input image.
            target_size (Tuple[int, int]): Target (width, height).
            resampling (int): Resampling method for resizing.

        Returns:
            Image.Image: Resized image.
        """
        if img.size == target_size:
            return img

        scale_factor = min(target_size[0] / img.width, target_size[1] / img.height)

        if scale_factor < 0.5:
            # Apply progressive downscaling to improve quality
            intermediate_size = (
                int(img.width * 0.707),  # Square root of 0.5
                int(img.height * 0.707)
            )
            img = img.resize(intermediate_size, Image.BOX)

        return img.resize(target_size, resampling)

    @staticmethod
    def create_white_transparent(img: Image.Image, threshold: int = 128) -> Image.Image:
        """
        Convert all non-transparent pixels to white while preserving transparency.

        Args:
            img (Image.Image): Input image.
            threshold (int): Alpha transparency threshold.

        Returns:
            Image.Image: Image with white non-transparent pixels.
        """
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        data = img.getdata()
        new_data = [
            (255, 255, 255, a) if a > threshold else (0, 0, 0, 0)
            for r, g, b, a in data
        ]

        white_img = Image.new('RGBA', img.size)
        white_img.putdata(new_data)
        return white_img

    @staticmethod
    def convert_image_mode(img: Image.Image, required_mode: str = "RGBA") -> Image.Image:
        """
        Convert an image to a required mode.

        Args:
            img (Image.Image): Input image.
            required_mode (str): Target mode (e.g., "RGBA", "RGB").

        Returns:
            Image.Image: Converted image.
        """
        if img.mode != required_mode:
            img = img.convert(required_mode)
        return img
