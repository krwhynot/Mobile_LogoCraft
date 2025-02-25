"""
Specialized test for CraveKit background removal method evaluation.
This test focuses exclusively on the neural network-based background removal
capabilities provided by the CarveKit library.
"""
import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path if needed
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Check if carvekit is installed
try:
    import torch
    from carvekit.api.high import HiInterface
    CARVEKIT_AVAILABLE = True
except ImportError:
    CARVEKIT_AVAILABLE = False
    logger.error("CarveKit library not found. Install with: pip install carvekit")
    logger.error("For CPU: pip install carvekit --extra-index-url https://download.pytorch.org/whl/cpu")
    logger.error("For GPU: pip install carvekit --extra-index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)


class CraveKitTester:
    """Test harness for CraveKit background removal methods"""
    
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        device: str = "cpu",
        file_extensions: List[str] = [".png", ".jpg", ".jpeg"]
    ):
        """
        Initialize the CraveKit tester.
        
        Args:
            input_dir: Directory containing test images
            output_dir: Directory for output images
            device: Device to use for processing (cpu, cuda)
            file_extensions: List of file extensions to process
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.device = device
        self.file_extensions = file_extensions
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Check device availability
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"
        
        logger.info(f"Initialized CraveKit tester with device: {self.device}")
        
        # Available models and their configurations
        self.model_configs = {
            "tracer_b7": {
                "seg_mask_size": 640,
                "trimap_dilation": 30,
                "trimap_erosion_iters": 5,
                "object_type": "object"
            },
            "u2net": {
                "seg_mask_size": 320,
                "trimap_dilation": 30,
                "trimap_erosion_iters": 5,
                "object_type": "hairs-like"
            },
            "basnet": {
                "seg_mask_size": 320,
                "trimap_dilation": 30,
                "trimap_erosion_iters": 5,
                "object_type": "object"
            },
            "deeplabv3": {
                "seg_mask_size": 1024,
                "trimap_dilation": 40,
                "trimap_erosion_iters": 20,
                "object_type": "object"
            }
        }
        
        # Interfaces for each model (lazy loaded)
        self.interfaces = {}
    
    def get_model_interface(self, model_name: str) -> HiInterface:
        """
        Get or create the interface for a specific model.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            Initialized HiInterface for the model
        """
        if model_name not in self.model_configs:
            raise ValueError(f"Unknown model: {model_name}")
        
        if model_name not in self.interfaces:
            config = self.model_configs[model_name]
            
            # Create the interface
            logger.info(f"Initializing {model_name} interface")
            
            # Use FP16 if using CUDA and have sufficient memory
            fp16 = False
            if self.device == "cuda" and torch.cuda.get_device_properties(0).total_memory > 8 * 1024 * 1024 * 1024:
                fp16 = True
                logger.info("Using FP16 precision")
            
            self.interfaces[model_name] = HiInterface(
                object_type=config["object_type"],
                batch_size_seg=1,
                batch_size_matting=1,
                device=self.device,
                seg_mask_size=config["seg_mask_size"],
                matting_mask_size=2048,
                trimap_prob_threshold=231,
                trimap_dilation=config["trimap_dilation"],
                trimap_erosion_iters=config["trimap_erosion_iters"],
                fp16=fp16
            )
        
        return self.interfaces[model_name]
    
    def process_image(
        self,
        image_path: Path,
        model_name: str
    ) -> Tuple[Image.Image, float]:
        """
        Process a single image with the specified model.
        
        Args:
            image_path: Path to the input image
            model_name: Name of the model to use
            
        Returns:
            Tuple of (processed image, execution time)
        """
        logger.info(f"Processing {image_path.name} with {model_name}")
        
        # Preprocess the image to ensure compatibility
        try:
            # Open the image and convert to RGB
            img = Image.open(image_path)
            
            # Convert to RGB if needed (CarveKit expects RGB images)
            if img.mode != 'RGB':
                if img.mode == 'RGBA':
                    # Create white background and composite
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha as mask
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Save to temporary file (CarveKit works better with files)
            temp_dir = Path(self.output_dir) / "temp"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = temp_dir / f"temp_{image_path.stem}.jpg"
            img.save(temp_path, format='JPEG', quality=95)
            
            # Get interface
            interface = self.get_model_interface(model_name)
            
            # Measure execution time
            start_time = time.time()
            
            # Process the image
            result_images = interface([str(temp_path)])
            result_image = result_images[0]
            
            elapsed_time = time.time() - start_time
            logger.info(f"  Completed in {elapsed_time:.2f}s")
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
                
            return result_image, elapsed_time
            
        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"  Failed in {elapsed_time:.2f}s: {e}")
            
            # Return original image with alpha channel and negative time to indicate error
            original = Image.open(image_path).convert("RGBA")
            return original, -elapsed_time
    
    def evaluate_quality(self, image: Image.Image) -> float:
        """
        Evaluate the quality of background removal.
        
        Args:
            image: Processed image with transparent background
            
        Returns:
            Quality score between 0 and 1 (higher is better)
        """
        # Convert to numpy array
        data = np.array(image)
        
        # Get alpha channel
        alpha = data[:, :, 3]
        
        # Count pixels with alpha > 0 (any visible content)
        visible_pixels = np.sum(alpha > 0)
        
        # Count pixels with alpha < 255 (any transparency)
        transparent_pixels = np.sum(alpha < 255)
        
        # Count total pixels
        total_pixels = alpha.size
        
        # Calculate ratios
        transparency_ratio = transparent_pixels / total_pixels if total_pixels > 0 else 0
        content_ratio = visible_pixels / total_pixels if total_pixels > 0 else 0
        
        # Balanced score: penalize if too little content or transparency
        if content_ratio < 0.05 or transparency_ratio < 0.05:
            return 0.0
        
        # Simple metric: how "balanced" the image is
        balance = 1.0 - abs(0.5 - transparency_ratio)
        
        return balance
    
    def run_test(self, models: List[str] = None) -> Dict:
        """
        Run tests for all specified models on all images.
        
        Args:
            models: List of models to test (defaults to all)
            
        Returns:
            Dictionary of test results
        """
        if models is None:
            models = list(self.model_configs.keys())
        
        # Validate models
        for model in models:
            if model not in self.model_configs:
                logger.error(f"Unknown model: {model}")
                models.remove(model)
        
        # Get all images to process
        image_files = []
        for ext in self.file_extensions:
            image_files.extend(list(self.input_dir.glob(f"*{ext}")))
        
        if not image_files:
            logger.error(f"No images found in {self.input_dir}")
            return {}
        
        logger.info(f"Found {len(image_files)} images to process")
        
        # Process each image with each model
        results = []
        
        for image_path in image_files:
            for model_name in models:
                # Process the image
                result_image, elapsed_time = self.process_image(image_path, model_name)
                
                # Skip if processing failed
                if elapsed_time < 0:
                    logger.warning(f"Skipping quality evaluation for failed processing: {image_path.name}, {model_name}")
                    continue
                
                # Save the result
                output_name = f"{image_path.stem}_{model_name}.png"
                output_path = self.output_dir / output_name
                result_image.save(output_path)
                
                # Evaluate quality
                quality_score = self.evaluate_quality(result_image)
                
                # Store result
                results.append({
                    "image": image_path.name,
                    "model": model_name,
                    "time": elapsed_time,
                    "quality": quality_score,
                    "output": output_path
                })
                
                logger.info(f"  Quality score: {quality_score:.2f}")
        
        # Generate summary
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> None:
        """
        Generate a report of test results.
        
        Args:
            results: List of test results
        """
        if not results:
            logger.error("No results to report")
            return
        
        report_path = self.output_dir / "cravekit_results.md"
        
        with open(report_path, 'w') as f:
            f.write("# CraveKit Background Removal Results\n\n")
            f.write(f"Test date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Device: {self.device}\n\n")
            
            # Overall summary
            f.write("## Summary\n\n")
            f.write("| Model | Avg. Time (s) | Avg. Quality |\n")
            f.write("|-------|--------------|-------------|\n")
            
            models = set(r["model"] for r in results)
            for model in sorted(models):
                model_results = [r for r in results if r["model"] == model]
                avg_time = sum(r["time"] for r in model_results) / len(model_results)
                avg_quality = sum(r["quality"] for r in model_results) / len(model_results)
                
                f.write(f"| {model} | {avg_time:.3f} | {avg_quality:.3f} |\n")
            
            # Per-image results
            f.write("\n## Results by Image\n\n")
            
            images = set(r["image"] for r in results)
            for image in sorted(images):
                f.write(f"### {image}\n\n")
                f.write("| Model | Time (s) | Quality |\n")
                f.write("|-------|----------|--------|\n")
                
                image_results = [r for r in results if r["image"] == image]
                for result in sorted(image_results, key=lambda r: r["model"]):
                    f.write(f"| {result['model']} | {result['time']:.3f} | {result['quality']:.3f} |\n")
                
                f.write("\n")
            
            # Model configurations
            f.write("\n## Model Configurations\n\n")
            for model, config in self.model_configs.items():
                if model in models:
                    f.write(f"### {model}\n\n")
                    f.write(f"- Object Type: {config['object_type']}\n")
                    f.write(f"- Segmentation Mask Size: {config['seg_mask_size']}\n")
                    f.write(f"- Trimap Dilation: {config['trimap_dilation']}\n")
                    f.write(f"- Trimap Erosion Iterations: {config['trimap_erosion_iters']}\n\n")
        
        logger.info(f"Report generated: {report_path}")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test CraveKit background removal methods")
    
    parser.add_argument("--input", type=str, 
                        default=str(Path(__file__).parent / "assets" / "test_images"),
                        help="Directory containing test images")
    
    parser.add_argument("--output", type=str, 
                        default=str(Path(__file__).parent / "assets" / "output" / "cravekit_only"),
                        help="Directory for output images")
    
    parser.add_argument("--device", type=str, choices=["cpu", "cuda"], default="cpu",
                        help="Device to use for processing")
    
    parser.add_argument("--models", type=str, nargs="+", 
                        choices=["tracer_b7", "u2net", "basnet", "deeplabv3", "all"],
                        default=["tracer_b7"],
                        help="Models to test")
    
    parser.add_argument("--extensions", type=str, nargs="+",
                        default=[".png", ".jpg", ".jpeg"],
                        help="File extensions to process")
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Process "all" models
    if "all" in args.models:
        args.models = ["tracer_b7", "u2net", "basnet", "deeplabv3"]
    
    # Create output directory and temp directory
    output_dir = Path(args.output)
    temp_dir = output_dir / "temp"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create tester
    tester = CraveKitTester(
        input_dir=Path(args.input),
        output_dir=output_dir,
        device=args.device,
        file_extensions=args.extensions
    )
    
    try:
        # Run tests
        results = tester.run_test(args.models)
        
        # Display summary
        if results:
            models = set(r["model"] for r in results)
            logger.info("\n=== RESULTS SUMMARY ===")
            
            for model in sorted(models):
                model_results = [r for r in results if r["model"] == model]
                avg_time = sum(r["time"] for r in model_results) / len(model_results)
                avg_quality = sum(r["quality"] for r in model_results) / len(model_results)
                
                logger.info(f"Model: {model}")
                logger.info(f"  Average Time: {avg_time:.2f}s")
                logger.info(f"  Average Quality: {avg_quality:.2f}")
            
            logger.info(f"\nResults saved to: {tester.output_dir}")
    
    finally:
        # Clean up temporary files
        if temp_dir.exists():
            for temp_file in temp_dir.glob("*.*"):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {e}")
            
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")


if __name__ == "__main__":
    main()
