from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional

from src.config.formats import ALLOWED_FORMATS, IMAGE_SETTINGS

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

# 5. **Channel Separation**
CHANNEL_SETTINGS = {
    'mode': 'RGBA',
    'channels': ['r', 'g', 'b', 'a']
}

# 6. **Grayscale Conversion**
GRAY_CONVERSION = {
    'to_rgb': cv2.COLOR_RGBA2RGB,
    'to_gray': cv2.COLOR_RGB2GRAY
}

# 7. **Contrast Analysis**
CONTRAST_SETTINGS = {
    'histogram_bins': 256,
    'range': [0, 256],
    'threshold': 0.5
}

# 8. **Blur Application**
BLUR_SETTINGS = {
    'kernel_size': (3, 3),
    'sigma': {'high_contrast': 0.5, 'low_contrast': 1.0}
}

# 9. **Edge Detection**
EDGE_SETTINGS = {
    'low_threshold': {'high_contrast': 30, 'low_contrast': 20},
    'high_threshold': {'high_contrast': 100, 'low_contrast': 90}
}

# 10. **Edge Dilation**
DILATION_SETTINGS = {
    'kernel_size': {'fine_text': (1, 1), 'normal': (2, 1)},
    'iterations': 1
}

# 11. **Adaptive Thresholding**
THRESHOLD_SETTINGS = {
    'method': cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    'type': cv2.THRESH_BINARY,
    'block_size': {'high_contrast': 7, 'low_contrast': 11},
    'C': 2
}

# 12. **Mask Combination**
COMBINE_SETTINGS = {
    'operation': cv2.bitwise_or,
    'threshold': 0  # For combined > 0
}

# 13. **Transparency Mask Creation**
MASK_SETTINGS = {
    'content_color': [255, 255, 255, 255],
    'background_color': [0, 0, 0, 0]
}

# 14. **Final Resize**
FINAL_RESIZE = {
    'target_size': (96, 96),
    'method': Image.LANCZOS
}

# 15. **Output Format Preparation**
FORMAT_SETTINGS = {
    'mode': 'RGBA',
    'background': (255, 255, 255, 0)
}

# 16. **File Saving**
SAVE_SETTINGS = {
    'format': 'PNG',
    'optimize': True,
    'quality': IMAGE_SETTINGS["quality"]
}


class PushProcessor:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

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

    def calculate_contrast(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, GRAY_CONVERSION['to_gray'])
        hist = cv2.calcHist([gray], [0], None, [CONTRAST_SETTINGS['histogram_bins']], CONTRAST_SETTINGS['range'])
        hist_norm = hist.ravel() / hist.sum()
        contrast = np.sqrt(np.sum(hist_norm * (np.arange(256) - hist_norm.mean()) ** 2))
        return contrast

    def create_coloring_book_effect(self, img: Image.Image) -> Image.Image:
        """
        Creates a bold black-and-white coloring book effect with a white background and strong edges.
        """
        img_array = np.array(img)

        # Extract alpha channel if present
        alpha = img_array[:, :, 3] if img_array.shape[2] == 4 else np.ones(img_array.shape[:2], dtype=np.uint8) * 255

        # Convert image to grayscale
        img_array = cv2.cvtColor(img_array, GRAY_CONVERSION['to_rgb'])
        gray = cv2.cvtColor(img_array, GRAY_CONVERSION['to_gray'])

        # Calculate image contrast
        contrast = self.calculate_contrast(img_array)
        high_contrast = contrast > CONTRAST_SETTINGS['threshold']

        # **1. Stronger Gaussian Blur to Reduce Noise**
        sigma = BLUR_SETTINGS['sigma']['high_contrast'] if high_contrast else BLUR_SETTINGS['sigma']['low_contrast']
        blurred = cv2.GaussianBlur(gray, BLUR_SETTINGS['kernel_size'], sigma)

        # **2. Higher Edge Detection Thresholds**
        thresholds = (
            (50, 150) if high_contrast else (30, 100)
        )
        edges = cv2.Canny(blurred, *thresholds)

        # **3. OTSU Threshold Instead of Adaptive**
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # **4. Combine Canny Edges with OTSU Threshold**
        combined = cv2.bitwise_or(edges, thresh)

        # **5. Invert the Image to Ensure White Background**
        inverted = cv2.bitwise_not(combined)  # <-- Fix: Invert colors

        # **6. Adaptive Dilation: Different Kernel for Bold and Fine Text**
        fine_text_kernel = np.ones((1, 1), np.uint8)  # Small kernel for fine text
        normal_text_kernel = np.ones((2, 2), np.uint8)  # Larger kernel for normal edges

        # Apply **small dilation for fine text** to keep details
        fine_text_dilated = cv2.dilate(inverted, fine_text_kernel, iterations=1)

        # Apply **larger dilation for bold text**
        normal_text_dilated = cv2.dilate(fine_text_dilated, normal_text_kernel, iterations=1)

        # **7. Create White Background with Black Edges**
        result = np.ones_like(img_array) * 255  # Set everything to white
        mask = normal_text_dilated > 0
        result[mask] = [0, 0, 0]  # Set edges to black

        # **8. Apply Transparency Mask**
        _, alpha_mask = cv2.threshold(alpha, 128, 255, cv2.THRESH_BINARY)
        rgba_result = np.zeros((*result.shape[:2], 4), dtype=np.uint8)
        rgba_result[:, :, :3] = result
        rgba_result[:, :, 3] = alpha_mask

        return Image.fromarray(rgba_result)

    def create_push_notification(self, input_path: Path, output_path: Path) -> Path:
        try:
            self.validate_file(input_path)

            with Image.open(input_path) as img:
                img = img.convert(MODE_SETTINGS['target_mode'])
                self.validate_dimensions(img)

                img = img.resize(INTERMEDIATE_RESIZE['target_size'], INTERMEDIATE_RESIZE['method'])

                processed = self.create_coloring_book_effect(img)

                final = processed.resize(FINAL_RESIZE['target_size'], FINAL_RESIZE['method'])

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