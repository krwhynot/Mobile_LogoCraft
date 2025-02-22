"""
Image Processing Service for managing image conversions.
"""
from pathlib import Path
import logging
from src.models.image_processor import ImageProcessor
from src.models.push_processor import PushProcessor
from src.models.base import BaseImageProcessor
from src.utils.logging import get_logger

class ImageProcessingService:
    """Handles batch processing of images and format management."""

    def __init__(self):
        """Initialize processors and load format configurations."""
        self.image_processor = ImageProcessor()
        self.push_processor = PushProcessor()
        self.logger = get_logger(__name__)
        self.formats = BaseImageProcessor.FORMAT_CONFIGS

    def process_batch(self, input_path: Path, output_dir: Path, selected_formats: set) -> list:
        """
        Process a batch of images into multiple formats.
        
        Args:
            input_path (Path): Path to the input image
            output_dir (Path): Directory for output files
            selected_formats (set): Set of format names to process
            
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
                result = self._process_single_format(input_path, output_dir, format_name)
                results.append(result)

            self._log_batch_results(results)
            return results

        except Exception as e:
            self.logger.error(f"Batch processing error: {e}")
            raise

    def _process_single_format(self, input_path: Path, output_dir: Path, format_name: str) -> dict:
        """
        Process an image into a single format.
        
        Args:
            input_path (Path): Path to input image
            output_dir (Path): Output directory
            format_name (str): Name of the format to process
            
        Returns:
            dict: Processing result with format, status, and output path
        """
        output_path = output_dir / f"{format_name}.PNG"
        
        try:
            if format_name == "PUSH":
                self.push_processor.create_push_notification(input_path, output_path)
            else:
                self.image_processor.process_format(input_path, output_path, format_name)

            return {
                "format": format_name,
                "status": "success",
                "output_path": str(output_path)
            }

        except Exception as e:
            self.logger.error(f"Error processing {format_name}: {e}")
            return {
                "format": format_name,
                "status": "failed",
                "error": str(e)
            }

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