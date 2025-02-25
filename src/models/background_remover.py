"""
Background removal implementation for the Mobile LogoCraft application.
Follows the complete background removal pipeline:
1. Contour Detection (Primary Method)
2. Thresholding (Secondary Refinement)
3. Mask Combination
4. Morphological Operations
5. Contour Refinement
6. Final Cleanup
7. Transparency Application
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
    COMBINED = "combined"  # Added combined method that follows the complete pipeline


class BackgroundRemover:
    """
    Handles background removal from images using various methods.
    Primary method is Contour Detection for optimal quality with app icons and logos.
    The COMBINED method follows the complete pipeline recommended in documentation:
    1. Contour Detection
    2. Thresholding
    3. Mask Combination
    4. Morphological Operations
    5. Contour Refinement
    6. Final Cleanup
    7. Transparency Application
    """
    
    def __init__(self, method: RemovalMethod = RemovalMethod.COMBINED):
        """
        Initialize the background remover with the specified method.
        
        Args:
            method: The method to use for background removal.
                   Defaults to COMBINED for optimal results with app icons.
        """
        self.method = method
        logger.info(f"Initialized BackgroundRemover with method: {method.value}")
    
    def remove_background(self, image: np.ndarray) -> np.ndarray:
        """
        Remove the background from an image using the selected method.
        This is the main entry point for background removal.
        
        Args:
            image: The input image as a numpy array (BGR format).
        
        Returns:
            Image with background removed as a numpy array with alpha channel (BGRA).
        """
        try:
            logger.info(f"Removing background using method: {self.method.value}")
            
            # First detect if the image has a white background
            has_white_bg = self.detect_white_background(image)
            
            # If no white background is detected, return original with alpha
            if not has_white_bg:
                logger.info("No white background detected, skipping background removal")
                return self._add_alpha_channel(image)
            
            # Apply the appropriate removal method
            if self.method == RemovalMethod.COMBINED:
                return self._remove_with_combined_pipeline(image)
            elif self.method == RemovalMethod.CONTOUR_DETECTION:
                return self._remove_with_contour_detection(image)
            elif self.method == RemovalMethod.THRESHOLD:
                return self._remove_with_threshold(image)
            elif self.method == RemovalMethod.CHROMA_KEY:
                return self._remove_with_chroma_key(image)
            elif self.method == RemovalMethod.GRABCUT:
                return self._remove_with_grabcut(image)
            else:
                # Default to combined pipeline if an invalid method is specified
                logger.warning(f"Invalid removal method: {self.method}, defaulting to combined pipeline")
                return self._remove_with_combined_pipeline(image)
                
        except Exception as e:
            logger.error(f"Error removing background: {str(e)}", exc_info=True)
            # Return original image with alpha channel
            return self._add_alpha_channel(image)
    
    def _remove_with_combined_pipeline(self, image: np.ndarray) -> np.ndarray:
        """
        Remove background using the complete pipeline as specified in documentation:
        1. Contour Detection (Primary Method)
        2. Thresholding (Secondary Refinement)
        3. Mask Combination
        4. Morphological Operations
        5. Contour Refinement
        6. Final Cleanup
        7. Transparency Application
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Image with transparent background (BGRA format).
        """
        logger.info("Applying complete background removal pipeline")
        
        # Step 1: Contour Detection (Primary Method)
        contour_mask = self._contour_detection_method(image)
        logger.debug("Step 1: Contour Detection completed")
        
        # Step 2: Thresholding (Secondary Refinement)
        threshold_mask = self._threshold_method(image)
        logger.debug("Step 2: Thresholding completed")
        
        # Step 3: Mask Combination
        combined_mask = self._combine_masks(contour_mask, threshold_mask)
        logger.debug("Step 3: Mask Combination completed")
        
        # Step 4: Morphological Operations
        morphed_mask = self._apply_morphological_operations(combined_mask)
        logger.debug("Step 4: Morphological Operations completed")
        
        # Step 5: Contour Refinement
        refined_mask = self._refine_contours(morphed_mask)
        logger.debug("Step 5: Contour Refinement completed")
        
        # Step 6: Final Cleanup
        cleaned_mask = self._final_cleanup(refined_mask)
        logger.debug("Step 6: Final Cleanup completed")
        
        # Step 7: Transparency Application
        result = self._apply_transparency(image, cleaned_mask)
        logger.debug("Step 7: Transparency Application completed")
        
        return result
    
    def _contour_detection_method(self, image: np.ndarray) -> np.ndarray:
        """
        Step 1: Contour Detection method to identify object boundaries.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Binary mask with detected objects.
        """
        # Convert the image to grayscale to simplify processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise and small details
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use Canny edge detection to find edges
        edges = cv2.Canny(blurred, 30, 150)
        
        # Dilate the edges to close small gaps
        dilated = cv2.dilate(edges, None, iterations=2)
        
        # Find contours in the edge map
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a mask by filling in the identified contours
        mask = np.zeros_like(gray)
        for contour in contours:
            if cv2.contourArea(contour) > 50:  # Filter small noise contours
                cv2.drawContours(mask, [contour], -1, 255, -1)
        
        return mask
    
    def _threshold_method(self, image: np.ndarray) -> np.ndarray:
        """
        Step 2: Apply thresholding to separate foreground from background.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Binary mask from thresholding.
        """
        # Convert to grayscale (if not already done)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to smooth the image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use Otsu's method to automatically determine optimal threshold value
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        return thresh
    
    def _combine_masks(self, mask1: np.ndarray, mask2: np.ndarray) -> np.ndarray:
        """
        Step 3: Combine masks from different methods to capture all foreground elements.
        
        Args:
            mask1: First binary mask.
            mask2: Second binary mask.
            
        Returns:
            Combined binary mask.
        """
        # Use bitwise OR to combine the masks
        # This ensures pixels identified as foreground by either method are preserved
        return cv2.bitwise_or(mask1, mask2)
    
    def _apply_morphological_operations(self, mask: np.ndarray) -> np.ndarray:
        """
        Step 4: Apply morphological operations to clean up the mask.
        
        Args:
            mask: Binary mask to process.
            
        Returns:
            Processed binary mask.
        """
        # Create a structural element (kernel) for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        # Apply morphological closing (dilation followed by erosion)
        # This helps connect nearby components and fill small holes
        closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return closed_mask
    
    def _refine_contours(self, mask: np.ndarray) -> np.ndarray:
        """
        Step 5: Further refine the mask by focusing on significant contours.
        
        Args:
            mask: Binary mask to refine.
            
        Returns:
            Refined binary mask.
        """
        # Find contours in the combined mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a clean mask with only significant contours
        refined_mask = np.zeros_like(mask)
        
        # Filter out small contours (noise)
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Adjust threshold as needed
                cv2.drawContours(refined_mask, [contour], 0, 255, -1)
        
        return refined_mask
    
    def _final_cleanup(self, mask: np.ndarray) -> np.ndarray:
        """
        Step 6: Final polish of the mask to ensure a clean result.
        
        Args:
            mask: Binary mask to clean up.
            
        Returns:
            Final cleaned binary mask.
        """
        # Apply additional morphological closing for final polish
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Fill any remaining small holes
        contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            cv2.drawContours(cleaned_mask, [contour], 0, 255, -1)
        
        return cleaned_mask
    
    def _apply_transparency(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Step 7: Create a transparent PNG with the background removed.
        
        Args:
            image: Original RGB image.
            mask: Binary mask representing the foreground.
            
        Returns:
            RGBA image with transparent background.
        """
        # Convert the original RGB image to RGBA (with alpha channel)
        rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        
        # Use the refined mask as the alpha channel
        rgba[:, :, 3] = mask
        
        return rgba
    
    def _remove_with_contour_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Remove background using only contour detection method.
        Optimized for logos and app icons with distinct edges.
        
        Args:
            image: The input image (BGR format).
            
        Returns:
            Image with transparent background (BGRA format).
        """
        # Get the mask from contour detection
        mask = self._contour_detection_method(image)
        
        # Apply basic cleanup
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Create output image with alpha channel
        result = self._apply_transparency(image, mask)
        
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
        # Get the mask from thresholding
        mask = self._threshold_method(image)
        
        # Create output image with alpha channel
        result = self._apply_transparency(image, mask)
        
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
        result = self._apply_transparency(image, mask)
        
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
        result = self._apply_transparency(image, grabcut_mask)
        
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