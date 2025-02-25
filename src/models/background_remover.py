"""
Background removal implementation for the Mobile LogoCraft application.
"""
import cv2
import numpy as np
from enum import Enum
from typing import Tuple, Optional
from pathlib import Path

from src.utils.logging import get_logger

logger = get_logger(__name__)


class RemovalMethod(Enum):
    """Enumeration of available background removal methods."""
    CONTOUR_DETECTION = "contour_detection"
    THRESHOLD = "threshold"
    CHROMA_KEY = "chroma_key"
    GRABCUT = "grabcut"


class BackgroundRemover:
    """
    Handles background removal from images using various methods.
    Primary method is Contour Detection for optimal quality with app icons and logos.
    """
    
    def __init__(self, method: RemovalMethod = RemovalMethod.CONTOUR_DETECTION):
        """
        Initialize the background remover with the specified method.
        
        Args:
            method: The method to use for background removal.
                   Defaults to Contour Detection for optimal results with app icons.
        """
        self.method = method
        logger.info(f"Initialized BackgroundRemover with method: {method.value}")
    
    def remove_background(self, image: np.ndarray) -> np.ndarray:
        """
        Remove the background from an image using the selected method.
        
        Args:
            image: The input image as a numpy array (BGR format).
        
        Returns:
            Image with background removed as a numpy array with alpha channel (BGRA).
        """
        try:
            logger.info(f"Removing background using method: {self.method.value}")
            
            if self.method == RemovalMethod.CONTOUR_DETECTION:
                return self._remove_with_contour_detection(image)
            elif self.method == RemovalMethod.THRESHOLD:
                return self._remove_with_threshold(image)
            elif self.method == RemovalMethod.CHROMA_KEY:
                return self._remove_with_chroma_key(image)
            elif self.method == RemovalMethod.GRABCUT:
                return self._remove_with_grabcut(image)
            else:
                # Default to contour detection if an invalid method is specified
                logger.warning(f"Invalid removal method: {self.method}, defaulting to contour detection")
                return self._remove_with_contour_detection(image)
                
        except Exception as e:
            logger.error(f"Error removing background: {str(e)}", exc_info=True)
            # Return original image with alpha channel
            return self._add_alpha_channel(image)
    
    def _remove_with_contour_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Remove background using contour detection method.
        Optimized for logos and app icons with distinct edges.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Image with transparent background (BGRA format).
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to create binary image
        _, thresh = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours in the threshold image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask with same dimensions as input image
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # Draw filled contours on mask
        cv2.drawContours(mask, contours, -1, 255, -1)
        
        # Apply morphological operations to improve mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Create output image with alpha channel
        height, width = image.shape[:2]
        result = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Copy BGR channels
        result[:, :, 0:3] = image
        
        # Set alpha channel from mask
        result[:, :, 3] = mask
        
        return result
    
    def _remove_with_threshold(self, image: np.ndarray) -> np.ndarray:
        """
        Remove background using simple thresholding.
        Fast but less precise than contour detection.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Image with transparent background (BGRA format).
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Create output image with alpha channel
        height, width = image.shape[:2]
        result = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Copy BGR channels
        result[:, :, 0:3] = image
        
        # Set alpha channel from mask
        result[:, :, 3] = mask
        
        return result
    
    def _remove_with_chroma_key(self, image: np.ndarray) -> np.ndarray:
        """
        Remove background using chroma key technique.
        Optimized for images with colored backgrounds.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Image with transparent background (BGRA format).
        """
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define white color range in HSV
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        
        # Create mask
        mask = cv2.inRange(hsv, lower_white, upper_white)
        mask = cv2.bitwise_not(mask)
        
        # Apply morphological operations
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Create output image with alpha channel
        height, width = image.shape[:2]
        result = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Copy BGR channels
        result[:, :, 0:3] = image
        
        # Set alpha channel from mask
        result[:, :, 3] = mask
        
        return result
    
    def _remove_with_grabcut(self, image: np.ndarray) -> np.ndarray:
        """
        Remove background using GrabCut algorithm.
        Most precise but slowest method, better for complex images.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Image with transparent background (BGRA format).
        """
        # Create initial mask
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Set rectangular region for foreground
        height, width = image.shape[:2]
        rect = (10, 10, width-20, height-20)
        
        # Create background/foreground model
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Apply GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        # Convert mask for display
        grabcut_mask = np.where((mask==2)|(mask==0), 0, 255).astype('uint8')
        
        # Create output image with alpha channel
        result = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Copy BGR channels
        result[:, :, 0:3] = image
        
        # Set alpha channel from mask
        result[:, :, 3] = grabcut_mask
        
        return result
    
    def _add_alpha_channel(self, image: np.ndarray) -> np.ndarray:
        """Add an alpha channel to an image without transparency."""
        if image.shape[2] == 3:  # BGR image
            height, width = image.shape[:2]
            result = np.zeros((height, width, 4), dtype=np.uint8)
            result[:, :, 0:3] = image
            result[:, :, 3] = 255  # Fully opaque
            return result
        return image  # Already has alpha channel
    
    @staticmethod
    def convert_to_white_icon(image: np.ndarray) -> np.ndarray:
        """
        Convert an image to white with transparency for the PUSH format.
        
        Args:
            image: The input image with alpha channel (BGRA format).
        
        Returns:
            White icon with transparency (BGRA format).
        """
        # Create a copy to avoid modifying the original
        result = image.copy()
        
        # Get the alpha channel
        alpha = result[:, :, 3]
        
        # Set all pixels to white where alpha is non-zero
        result[:, :, 0:3][alpha > 0] = [255, 255, 255]
        
        return result
    
    @staticmethod
    def detect_white_background(image: np.ndarray, threshold: int = 240, coverage: float = 0.9) -> bool:
        """
        Detect if an image has a predominantly white background.
        
        Args:
            image: The input image (BGR format).
            threshold: Pixel value threshold to consider as white (0-255).
            coverage: Required percentage of white pixels to consider as white background.
            
        Returns:
            True if the image has a white background, False otherwise.
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate percentage of white pixels in the image border
        h, w = gray.shape
        border_pixels = np.concatenate([
            gray[0, :],      # top row
            gray[-1, :],     # bottom row
            gray[1:-1, 0],   # left column (excluding corners)
            gray[1:-1, -1]   # right column (excluding corners)
        ])
        
        white_pixels = np.sum(border_pixels >= threshold)
        white_percentage = white_pixels / len(border_pixels)
        
        logger.debug(f"White background detection: {white_percentage:.2f} (threshold: {coverage})")
        return white_percentage >= coverage
