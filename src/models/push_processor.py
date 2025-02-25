from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional

from src.config.formats import ALLOWED_FORMATS, IMAGE_SETTINGS
from src.models.background_remover import BackgroundRemover

# 1. **Initial File Validation**
FILE_VALIDATION = {
    'max_file_size': IMAGE_SETTINGS["max_file_size"],
    'allowed_formats': ALLOWED_FORMATS,
    'chunk_size': 1024 * 1024  # File reading buffer
}

# 2. **Dimension Validation**
DIMENSION_VALIDATION = {
    'min_dimension': IMAGE_SETTINGS["min_dimension"],
    'max_dimension': IMAGE_SETTINGS["max_dimension"],
    'push_min_size': (64, 64)
}

# 3. **Image Mode Conversion**
MODE_SETTINGS = {
    'target_mode': 'RGBA',
    'alpha_handling': True
}

# 4. **Initial Size Adjustment**
INTERMEDIATE_RESIZE = {
    'target_size': (192, 192),
    'method': Image.LANCZOS
}

# 5. **Grayscale Conversion**
GRAY_CONVERSION = {
    'to_rgb': cv2.COLOR_RGBA2RGB,
    'to_gray': cv2.COLOR_RGB2GRAY
}

# 6. **Final Resize**
FINAL_RESIZE = {
    'target_size': (96, 96),
    'method': Image.LANCZOS
}

# 7. **Output Format Preparation**
FORMAT_SETTINGS = {
    'mode': 'RGBA',
    'background': (255, 255, 255, 0)
}

# 8. **File Saving**
SAVE_SETTINGS = {
    'format': 'PNG',
    'optimize': True,
    'quality': IMAGE_SETTINGS["quality"]
}


class PushProcessor:
    def __init__(self, logger: Optional[logging.Logger] = None, background_remover: Optional[BackgroundRemover] = None):
        self.logger = logger or logging.getLogger(__name__)
        # Use the provided background_remover or create a new one
        self.background_remover = background_remover or BackgroundRemover()

    def validate_file(self, file_path: Path) -> bool:
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in FILE_VALIDATION['allowed_formats']:
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        if file_path.stat().st_size > FILE_VALIDATION['max_file_size']:
            raise ValueError(f"File too large: {file_path.stat().st_size / (1024 * 1024):.1f}MB")

        return True

    def validate_dimensions(self, image: Image.Image) -> bool:
        width, height = image.size
        if width < DIMENSION_VALIDATION['min_dimension'] or height < DIMENSION_VALIDATION['min_dimension']:
            raise ValueError(f"Image too small: {width}x{height}")

        if width > DIMENSION_VALIDATION['max_dimension'] or height > DIMENSION_VALIDATION['max_dimension']:
            raise ValueError(f"Image too large: {width}x{height}")

        return True

    def create_coloring_book_effect(self, img: Image.Image) -> Image.Image:
        """
        Creates a bold black-and-white coloring book effect with a white background and strong edges.
        Note: This doesn't remove the background - it creates a specialized visual effect.
        """
        img_array = np.array(img)

        # Extract alpha channel if present
        alpha = img_array[:, :, 3] if img_array.shape[2] == 4 else np.ones(img_array.shape[:2], dtype=np.uint8) * 255

        # Convert image to grayscale
        img_array = cv2.cvtColor(img_array, GRAY_CONVERSION['to_rgb'])
        gray = cv2.cvtColor(img_array, GRAY_CONVERSION['to_gray'])

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (3, 3), 0.8)

        # Apply OTSU Threshold
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find edges
        edges = cv2.Canny(blurred, 30, 100)

        # Combine edges with threshold
        combined = cv2.bitwise_or(edges, thresh)

        # Invert to ensure white background
        inverted = cv2.bitwise_not(combined)

        # Apply dilation to enhance edges
        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(inverted, kernel, iterations=1)

        # Create white background with black edges
        result = np.ones_like(img_array) * 255  # Set everything to white
        mask = dilated > 0
        result[mask] = [0, 0, 0]  # Set edges to black

        # Apply original transparency mask
        _, alpha_mask = cv2.threshold(alpha, 128, 255, cv2.THRESH_BINARY)
        rgba_result = np.zeros((*result.shape[:2], 4), dtype=np.uint8)
        rgba_result[:, :, :3] = result
        rgba_result[:, :, 3] = alpha_mask

        return Image.fromarray(rgba_result)

    def create_push_notification(self, input_path: Path, output_path: Path, remove_background: bool = False) -> Path:
        """
        Process an image into a PUSH notification icon.
        
        Args:
            input_path: Path to the input image
            output_path: Path where the output image will be saved
            remove_background: Whether to perform background removal (from checkbox selection)
            
        Returns:
            Path to the processed image
        """
        try:
            self.logger.info(f"Processing push notification icon. Background removal: {remove_background}")
            self.validate_file(input_path)

            # Open the image
            with Image.open(input_path) as img:
                img = img.convert(MODE_SETTINGS['target_mode'])
                self.validate_dimensions(img)

                # Resize to intermediate size for processing
                img = img.resize(INTERMEDIATE_RESIZE['target_size'], INTERMEDIATE_RESIZE['method'])
                
                # STEP 1: Background removal if enabled (from UI checkbox)
                # Delegate ALL background removal to the BackgroundRemover class
                if remove_background:
                    self.logger.info("STEP 1: Applying background removal using BackgroundRemover...")
                    
                    # Convert PIL image to CV2 format for background removal
                    img_array = np.array(img)
                    cv2_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
                    
                    # Pass to the background remover without additional checks
                    # Let the BackgroundRemover handle all logic related to background detection and removal
                    removed_bg = self.background_remover.remove_background(cv2_img[:, :, :3])
                    
                    # Convert back to PIL for further processing
                    img = Image.fromarray(cv2.cvtColor(removed_bg, cv2.COLOR_BGRA2RGBA))
                
                # STEP 2: Apply coloring book effect (specialized push notification style)
                # This creates the distinctive black and white effect required for push notification icons
                self.logger.info("STEP 2: Applying push notification styling...")
                processed = self.create_coloring_book_effect(img)
                
                # STEP 3: Final resize to target dimensions
                self.logger.info("STEP 3: Resizing to final dimensions...")
                final = processed.resize(FINAL_RESIZE['target_size'], FINAL_RESIZE['method'])

                # Save the resulting image
                final.save(
                    output_path, 
                    SAVE_SETTINGS['format'], 
                    optimize=SAVE_SETTINGS['optimize'],
                    quality=SAVE_SETTINGS['quality']
                )

            self.logger.info(f"Successfully created push notification icon: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error processing push icon: {str(e)}")
            raise