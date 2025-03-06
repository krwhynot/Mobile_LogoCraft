"""
Image Processing Service for managing image conversions.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

from src.models.image_processor import ImageProcessor
from src.models.push_processor import PushProcessor
from src.models.base import BaseImageProcessor
from src.models.background_remover import BackgroundRemover
from src.utils.logging import get_logger

class ImageProcessingService:
    """Handles batch processing of images and format management."""

    def __init__(self):
        """Initialize processors and load format configurations."""
        self.logger = get_logger(__name__)
        self.background_remover = BackgroundRemover()
        self.image_processor = ImageProcessor()
        # Pass the existing background_remover instance to PushProcessor
        self.push_processor = PushProcessor(background_remover=self.background_remover)
        self.formats = BaseImageProcessor.FORMAT_CONFIGS

    def process_batch(self, input_path: Path, output_dir: Path, selected_formats: set, remove_background: bool = False) -> list:
        """
        Process a batch of images into multiple formats.
        
        Args:
            input_path (Path): Path to the input image
            output_dir (Path): Directory for output files
            selected_formats (set): Set of format names to process
            remove_background (bool): Whether to remove white backgrounds
            
        Returns:
            list: List of dictionaries containing processing results
        """
        try:
            input_path = Path(input_path)
            output_dir = Path(output_dir)

            if not input_path.is_file():
                raise ValueError(f"Invalid input file: {input_path}")

            output_dir.mkdir(parents=True, exist_ok=True)

            results = []
            for format_name in selected_formats:
                result = self._process_single_format(input_path, output_dir, format_name, remove_background)
                results.append(result)

            self._log_batch_results(results)
            return results

        except Exception as e:
            self.logger.error(f"Batch processing error: {e}", exc_info=True)
            raise
    
    def process_single_format(self, input_path: Path, output_dir: Path, format_name: str, remove_background: bool = False) -> dict:
        """
        Process an image into a single format, suitable for individual processing with progress tracking.
        
        Args:
            input_path (Path): Path to input image
            output_dir (Path): Output directory
            format_name (str): Name of the format to process
            remove_background (bool): Whether to remove white backgrounds
            
        Returns:
            dict: Processing result with format, status, and output path
        """
        return self._process_single_format(input_path, output_dir, format_name, remove_background)

    def _process_single_format(self, input_path: Path, output_dir: Path, format_name: str, remove_background: bool = False) -> dict:
        """
        Process an image into a single format.
        
        Args:
            input_path (Path): Path to input image
            output_dir (Path): Output directory
            format_name (str): Name of the format to process
            remove_background (bool): Whether to remove white backgrounds
            
        Returns:
            dict: Processing result with format, status, and output path
        """
        output_path = output_dir / f"{format_name}.PNG"
        
        try:
            # Handle PUSH format with our updated processor that handles background removal internally
            if format_name == "PUSH":
                self.logger.info(f"Processing PUSH format with background removal={remove_background}")
                self.push_processor.create_push_notification(input_path, output_path, remove_background)
                return {
                    "format": format_name,
                    "status": "success",
                    "output_path": str(output_path)
                }
            
            # For other formats, use the existing background removal logic
            # Read the input image
            img = cv2.imread(str(input_path))
            if img is None:
                raise ValueError(f"Failed to load image: {input_path}")
            
            # Apply background removal if enabled and format supports transparency
            supports_transparency = format_name in ["LOGO", "LOGO_WIDE", "APPICON"]
            has_white_bg = False
            
            if remove_background and supports_transparency:
                # Check if the image has a white background
                has_white_bg = self.background_remover.detect_white_background(img)
                
                if has_white_bg:
                    self.logger.info(f"Removing white background for {format_name}")
                    img = self.background_remover.remove_background(img)
            
            # Handle special cases with specific processors
            if format_name == "LOGO_WIDE":
                # Use the specialized logo processor method for wide format
                if remove_background and has_white_bg:
                    # For LOGO_WIDE with background removal, we need to resize it correctly
                    # Get the format configuration
                    config = self.formats[format_name]
                    target_width, target_height = config["size"]
                    
                    # Convert OpenCV image to PIL for processing
                    img_pil = self._convert_cv_to_pil(img)
                    
                    # Process the image to the correct dimensions
                    self.image_processor.process_image(
                        input_path=None,  # Not used when providing img_pil directly
                        output_path=output_path,
                        width=target_width,
                        height=target_height,
                        bg_color=config["bg_color"],
                        img_pil=img_pil
                    )
                else:
                    self.image_processor.process_logo(input_path, output_path, wide=True)
            elif format_name == "LOGO":
                # Use the specialized logo processor method for square format
                if remove_background and has_white_bg:
                    # For LOGO with background removal, we need to resize it correctly
                    # Get the format configuration
                    config = self.formats[format_name]
                    target_width, target_height = config["size"]
                    
                    # Convert OpenCV image to PIL for processing
                    img_pil = self._convert_cv_to_pil(img)
                    
                    # Process the image to the correct dimensions
                    self.image_processor.process_image(
                        input_path=None,  # Not used when providing img_pil directly
                        output_path=output_path,
                        width=target_width,
                        height=target_height,
                        bg_color=config["bg_color"],
                        img_pil=img_pil
                    )
                else:
                    self.image_processor.process_logo(input_path, output_path, wide=False)
            else:
                # Process all other formats normally
                if format_name == "APPICON" and remove_background and has_white_bg:
                    # For APPICON with background removal, we need to resize it correctly
                    # Get the format configuration
                    config = self.formats[format_name]
                    target_width, target_height = config["size"]
                    
                    # Convert OpenCV image to PIL for processing
                    img_pil = self._convert_cv_to_pil(img)
                    
                    # Process the image to the correct dimensions
                    self.image_processor.process_image(
                        input_path=None,  # Not used when providing img_pil directly
                        output_path=output_path,
                        width=target_width,
                        height=target_height,
                        bg_color=config["bg_color"],
                        img_pil=img_pil
                    )
                else:
                    self.image_processor.process_format(input_path, output_path, format_name)

            self.logger.info(f"Successfully processed format {format_name} to {output_path}")

            return {
                "format": format_name,
                "status": "success",
                "output_path": str(output_path)
            }

        except Exception as e:
            self.logger.error(f"Error processing {format_name}: {e}", exc_info=True)
            return {
                "format": format_name,
                "status": "failed",
                "error": str(e)
            }

    def _convert_cv_to_pil(self, img: np.ndarray) -> Image.Image:
        """
        Convert OpenCV image to PIL Image.
        
        Args:
            img: OpenCV image (BGR or BGRA format)
            
        Returns:
            PIL Image (RGB or RGBA format)
        """
        try:
            if img.shape[2] == 4:  # If has alpha channel
                b, g, r, a = cv2.split(img)
                return Image.fromarray(cv2.merge((r, g, b, a)), 'RGBA')
            else:
                return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        except Exception as e:
            self.logger.error(f"Error converting CV to PIL: {e}", exc_info=True)
            # Fallback to RGB conversion
            return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    def _log_batch_results(self, results: list) -> None:
        """Log the results of batch processing."""
        successful = [r["format"] for r in results if r["status"] == "success"]
        failed = [r["format"] for r in results if r["status"] == "failed"]
        
        if successful:
            self.logger.info(f"Successfully processed formats: {', '.join(successful)}")
        if failed:
            self.logger.error(f"Failed to process formats: {', '.join(failed)}")

    def get_available_formats(self) -> dict:
        """
        Get all available format configurations.
        
        Returns:
            dict: Format names and their configurations
        """
        return self.formats

    def validate_format(self, format_name: str) -> bool:
        """
        Check if a format name is valid.
        
        Args:
            format_name (str): Name of the format to validate
            
        Returns:
            bool: True if format exists, False otherwise
        """
        return format_name in self.formats