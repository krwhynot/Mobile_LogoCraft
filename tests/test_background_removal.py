"""
Test file for evaluating different background removal methods
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
from PIL import Image
import cv2

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

from src.models.base import BaseImageProcessor


class BackgroundRemovalMethod:
    """Base class for background removal methods"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from image, override in subclasses"""
        raise NotImplementedError("Background removal method not implemented")
        
    def get_info(self) -> Dict:
        """Return information about this method"""
        return {
            "name": self.name,
            "description": self.description
        }


class ThresholdRemovalMethod(BackgroundRemovalMethod):
    """Remove background using color thresholding"""
    
    def __init__(self, threshold: int = 240, tolerance: int = 30):
        super().__init__(
            name="Color Threshold",
            description="Removes background using simple color thresholding"
        )
        self.threshold = threshold
        self.tolerance = tolerance
        
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove white background using simple thresholding"""
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Convert to numpy array for processing
        data = np.array(image)
        
        # Create alpha mask based on RGB values close to white
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        
        # Compute the "whiteness" of each pixel
        # A pixel is considered white if all RGB values are above threshold
        white_mask = (r > self.threshold) & (g > self.threshold) & (b > self.threshold)
        
        # Create a gradient alpha based on how close to white
        color_distance = np.sqrt((255-r)**2 + (255-g)**2 + (255-b)**2)
        alpha_factor = np.clip(color_distance / self.tolerance, 0, 1)
        
        # Apply the alpha mask (0 for white background, 255 for foreground)
        data[:,:,3] = np.where(
            white_mask, 
            np.zeros_like(a),  # Background: transparent
            a * alpha_factor    # Foreground: keep original alpha * factor
        )
        
        return Image.fromarray(data)


class ChromaKeyRemovalMethod(BackgroundRemovalMethod):
    """Remove background using chroma key technique"""
    
    def __init__(self, target_color: Tuple[int, int, int] = (255, 255, 255), tolerance: int = 30):
        super().__init__(
            name="Chroma Key",
            description="Removes background using chroma key technique similar to green screen"
        )
        self.target_color = target_color
        self.tolerance = tolerance
        
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background using chroma key technique"""
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Convert to numpy array for processing
        data = np.array(image)
        
        # Calculate Euclidean distance from target color
        r, g, b = data[:,:,0], data[:,:,1], data[:,:,2]
        distance = np.sqrt(
            (r - self.target_color[0])**2 +
            (g - self.target_color[1])**2 +
            (b - self.target_color[2])**2
        )
        
        # Create normalized alpha channel based on distance
        alpha = np.clip(distance / self.tolerance, 0, 1) * 255
        
        # Apply to alpha channel
        data[:,:,3] = alpha.astype(np.uint8)
        
        return Image.fromarray(data)


class ContourBasedRemovalMethod(BackgroundRemovalMethod):
    """Remove background using contour detection"""
    
    def __init__(self, threshold: int = 240, blur_size: int = 3):
        super().__init__(
            name="Contour Detection",
            description="Removes background by detecting object contours"
        )
        self.threshold = threshold
        self.blur_size = blur_size
        
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background using contour detection"""
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Convert PIL image to OpenCV format
        img_array = np.array(image)
        
        # Handle the case where the image doesn't have an alpha channel
        if img_array.shape[2] < 4:
            img_array = np.concatenate(
                [img_array, np.ones((*img_array.shape[:2], 1), dtype=np.uint8) * 255], 
                axis=2
            )
        
        # Extract alpha channel
        alpha = img_array[:, :, 3].copy()
        
        # Convert to BGR for OpenCV
        bgr = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, self.threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask
        mask = np.zeros(gray.shape, np.uint8)
        
        # Draw contours on mask
        cv2.drawContours(mask, contours, -1, 255, -1)
        
        # Refine mask with additional morphological operations
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Apply mask to alpha channel
        img_array[:, :, 3] = mask
        
        return Image.fromarray(img_array)


class GrabCutRemovalMethod(BackgroundRemovalMethod):
    """Remove background using GrabCut algorithm"""
    
    def __init__(self, margin: int = 1, iterations: int = 5):
        super().__init__(
            name="GrabCut",
            description="Removes background using GrabCut segmentation algorithm"
        )
        self.margin = margin
        self.iterations = iterations
        
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background using GrabCut algorithm"""
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Convert PIL image to OpenCV format
        img_array = np.array(image)
        
        # Extract RGB part for GrabCut
        img_rgb = img_array[:, :, :3]
        
        # Create a mask initialized with obvious background and probable foreground
        mask = np.zeros(img_rgb.shape[:2], np.uint8)
        
        # Set mask border pixels as definite background
        height, width = mask.shape
        border_width = max(width // 10, 1)
        
        # Mark borders as definite background (0)
        mask[:border_width, :] = 0
        mask[-border_width:, :] = 0
        mask[:, :border_width] = 0
        mask[:, -border_width:] = 0
        
        # Mark center area as probable foreground (3)
        center_margin = max(self.margin, border_width)
        mask[center_margin:-center_margin, center_margin:-center_margin] = 3
        
        # Create temporary arrays for GrabCut
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Convert to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        # Apply GrabCut
        rect = (border_width, border_width, width - 2*border_width, height - 2*border_width)
        cv2.grabCut(img_bgr, mask, rect, bgd_model, fgd_model, self.iterations, cv2.GC_INIT_WITH_MASK)
        
        # Create mask where foreground (1) and probable foreground (3) are white
        mask_binary = np.where((mask == 1) | (mask == 3), 255, 0).astype('uint8')
        
        # Apply mask to alpha channel
        img_array[:, :, 3] = mask_binary
        
        return Image.fromarray(img_array)


def evaluate_transparency(image: Image.Image) -> float:
    """
    Evaluate the quality of background removal by checking transparency
    Returns a score between 0 and 1 (higher is better)
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
    
    # Calculate various metrics
    transparency_ratio = transparent_pixels / total_pixels if total_pixels > 0 else 0
    content_ratio = visible_pixels / total_pixels if total_pixels > 0 else 0
    
    # For ideal background removal:
    # - We want some visible content (content_ratio > 0)
    # - We want some transparency (transparency_ratio > 0)
    # - We don't want all pixels to be either fully opaque or fully transparent
    
    # Simple metric: how "balanced" the image is between content and transparency
    balance = 1.0 - abs(0.5 - transparency_ratio)
    
    # Adjusted score: penalize if the image has too little content or transparency
    min_content_threshold = 0.05
    min_transparency_threshold = 0.05
    
    if content_ratio < min_content_threshold or transparency_ratio < min_transparency_threshold:
        return 0.0
    
    return balance


def get_method_pros_cons(method_name: str) -> Tuple[List[str], List[str]]:
    """
    Get pros and cons for a given method
    Returns: (pros, cons)
    """
    method_pros_cons = {
        "Color Threshold": (
            [
                "Fast execution speed",
                "Very simple implementation",
                "Works well for images with uniform white backgrounds",
                "Low memory requirements",
                "No dependencies beyond NumPy and PIL"
            ],
            [
                "Not effective for complex backgrounds",
                "Struggles with shadows and gradients",
                "Sensitive to white/near-white objects in foreground",
                "Limited control over edge quality",
                "Cannot handle varied background colors"
            ]
        ),
        "Chroma Key": (
            [
                "Relatively fast processing",
                "Works with any background color (not just white)",
                "Better handling of semi-transparent edges",
                "Good for product images with solid backgrounds",
                "Adjustable tolerance for different scenarios"
            ],
            [
                "Still sensitive to colors similar to background in foreground objects",
                "May struggle with reflections and shadows",
                "Requires tuning for different images",
                "Not suitable for complex or varied backgrounds",
                "Can create artifacts around edges"
            ]
        ),
        "Contour Detection": (
            [
                "Better edge detection and preservation",
                "Less affected by shadows than simple thresholding",
                "Can handle slightly textured backgrounds",
                "Good for logos and illustrations",
                "More robust to lighting variations"
            ],
            [
                "Slower than thresholding methods",
                "Struggles with intricate details",
                "OpenCV dependency required",
                "Can merge nearby objects into single contours",
                "Not ideal for highly detailed or natural images"
            ]
        ),
        "GrabCut": (
            [
                "Most sophisticated segmentation algorithm",
                "Best handling of complex objects and backgrounds",
                "Can extract objects from non-uniform backgrounds",
                "Preserves intricate details and edges",
                "Works well for natural images and photographs"
            ],
            [
                "Slowest execution time",
                "Highest computational requirements",
                "Results can be unpredictable",
                "May require multiple iterations for best results",
                "OpenCV dependency with more complex implementation"
            ]
        )
    }
    
    return method_pros_cons.get(method_name, ([], []))


def save_results_report(results: List[Dict], output_dir: Path) -> None:
    """Save results to a markdown report file"""
    report_path = output_dir / "background_removal_results.md"
    
    with open(report_path, 'w') as f:
        f.write("# Background Removal Test Results\n\n")
        
        # Summary by method
        f.write("## Summary by Method\n\n")
        f.write("| Method | Avg. Time (s) | Avg. Quality |\n")
        f.write("|--------|--------------|-------------|\n")
        
        methods = set(r["method"] for r in results)
        for method in sorted(methods):
            method_results = [r for r in results if r["method"] == method]
            avg_time = sum(r["execution_time"] for r in method_results) / len(method_results)
            avg_quality = sum(r["quality_score"] for r in method_results) / len(method_results)
            f.write(f"| {method} | {avg_time:.3f} | {avg_quality:.3f} |\n")
        
        f.write("\n")
        
        # Detailed results by image
        f.write("## Detailed Results\n\n")
        
        images = set(r["image"] for r in results)
        for image in sorted(images):
            f.write(f"### {image}\n\n")
            f.write("| Method | Time (s) | Quality | Output |\n")
            f.write("|--------|----------|---------|--------|\n")
            
            image_results = [r for r in results if r["image"] == image]
            for result in sorted(image_results, key=lambda r: r["method"]):
                rel_path = os.path.relpath(result["output_path"], output_dir)
                f.write(f"| {result['method']} | {result['execution_time']:.3f} | " +
                        f"{result['quality_score']:.3f} | [{rel_path}]({rel_path}) |\n")
            
            f.write("\n")
        
        # Method descriptions
        f.write("## Method Descriptions\n\n")
        
        methods_info = [
            ThresholdRemovalMethod(),
            ChromaKeyRemovalMethod(),
            ContourBasedRemovalMethod(),
            GrabCutRemovalMethod()
        ]
        
        for method in methods_info:
            f.write(f"### {method.name}\n\n")
            f.write(f"{method.description}\n\n")
            
            # Add pros and cons
            pros, cons = get_method_pros_cons(method.name)
            
            f.write("**Pros:**\n\n")
            for pro in pros:
                f.write(f"- {pro}\n")
            f.write("\n")
            
            f.write("**Cons:**\n\n")
            for con in cons:
                f.write(f"- {con}\n")
            f.write("\n")
        
    logger.info(f"Results report saved to: {report_path}")


def get_background_removal_method(method_name: str) -> Optional[BackgroundRemovalMethod]:
    """
    Factory function to get a background removal method by name
    
    Args:
        method_name: Name of the method to retrieve
        
    Returns:
        BackgroundRemovalMethod instance or None if not found
    """
    methods = {
        "threshold": ThresholdRemovalMethod(),
        "chroma_key": ChromaKeyRemovalMethod(),
        "contour": ContourBasedRemovalMethod(),
        "grabcut": GrabCutRemovalMethod()
    }
    
    return methods.get(method_name.lower())


def remove_background(image: Image.Image, method: str = "threshold", **kwargs) -> Image.Image:
    """
    Utility function to remove background from an image
    
    Args:
        image: Input PIL image
        method: Method name to use
        **kwargs: Additional parameters for the method
        
    Returns:
        PIL image with background removed
    """
    # Get the method
    removal_method = get_background_removal_method(method)
    
    if removal_method is None:
        raise ValueError(f"Unknown background removal method: {method}")
    
    # Set custom parameters if provided
    for key, value in kwargs.items():
        if hasattr(removal_method, key):
            setattr(removal_method, key, value)
    
    # Process the image
    return removal_method.remove_background(image)


def test_all_methods_all_images():
    """Test all methods on all test images"""
    # Set paths
    test_dir = Path(__file__).parent
    test_images_dir = test_dir / 'assets' / 'test_images'
    output_dir = test_dir / 'assets' / 'output' / 'background_removal'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define test methods
    methods = [
        ThresholdRemovalMethod(),
        ChromaKeyRemovalMethod(),
        ContourBasedRemovalMethod(),
        GrabCutRemovalMethod()
    ]
    
    # Get all PNG images in test directory
    image_files = list(test_images_dir.glob('*.png'))
    
    # Check if we have test images
    if len(image_files) == 0:
        logger.error("No test images found")
        return
    
    # Prepare results
    results = []
    
    # Process each image with each method
    for image_path in image_files:
        logger.info(f"Processing image: {image_path.name}")
        
        # Load the image
        image = Image.open(image_path)
        
        # Process with each method
        for method in methods:
            logger.info(f"  Using method: {method.name}")
            
            # Measure performance
            start_time = time.time()
            result_image = method.remove_background(image)
            elapsed_time = time.time() - start_time
            
            # Save result
            output_path = output_dir / f"{image_path.stem}_{method.name.replace(' ', '_').lower()}.png"
            result_image.save(output_path)
            
            # Evaluate quality by checking transparency
            quality_score = evaluate_transparency(result_image)
            
            # Store results
            results.append({
                "image": image_path.name,
                "method": method.name,
                "execution_time": elapsed_time,
                "quality_score": quality_score,
                "output_path": output_path
            })
            
            logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}, Output: {output_path}")
    
    # Log summary
    if results:
        logger.info("\n=== RESULTS SUMMARY ===")
        
        # Group by method
        methods = set(r["method"] for r in results)
        
        for method in methods:
            method_results = [r for r in results if r["method"] == method]
            avg_time = sum(r["execution_time"] for r in method_results) / len(method_results)
            avg_quality = sum(r["quality_score"] for r in method_results) / len(method_results)
            
            logger.info(f"Method: {method}")
            logger.info(f"  Average Time: {avg_time:.2f}s")
            logger.info(f"  Average Quality: {avg_quality:.2f}")
    
    # Save results to report file
    save_results_report(results, output_dir)
    logger.info(f"Testing completed. Results saved to {output_dir}")


# Check if carvekit is available for comparison
try:
    from test_cravekit_removal import CraveKitRemovalMethod
    CARVEKIT_AVAILABLE = True
except ImportError:
    CARVEKIT_AVAILABLE = False
    logger.info("CarveKit not available for comparison. Install with: pip install carvekit")


def test_all_methods_all_images(include_carvekit=False):
    """Test all methods on all test images"""
    # Set paths
    test_dir = Path(__file__).parent
    test_images_dir = test_dir / 'assets' / 'test_images'
    output_dir = test_dir / 'assets' / 'output' / 'background_removal'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define test methods
    methods = [
        ThresholdRemovalMethod(),
        ChromaKeyRemovalMethod(),
        ContourBasedRemovalMethod(),
        GrabCutRemovalMethod()
    ]
    
    # Add CraveKit method if available and requested
    if include_carvekit and CARVEKIT_AVAILABLE:
        try:
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            methods.append(CraveKitRemovalMethod(model_type="tracer_b7", device=device))
            logger.info("Added CraveKit method with model type: tracer_b7")
        except Exception as e:
            logger.error(f"Failed to initialize CraveKit method: {e}")
    
    # Get all PNG images in test directory
    image_files = list(test_images_dir.glob('*.png'))
    
    # Check if we have test images
    if len(image_files) == 0:
        logger.error("No test images found")
        return
    
    # Prepare results
    results = []
    
    # Process each image with each method
    for image_path in image_files:
        logger.info(f"Processing image: {image_path.name}")
        
        # Load the image
        image = Image.open(image_path)
        
        # Process with each method
        for method in methods:
            logger.info(f"  Using method: {method.name}")
            
            # Measure performance
            start_time = time.time()
            result_image = method.remove_background(image)
            elapsed_time = time.time() - start_time
            
            # Save result
            output_path = output_dir / f"{image_path.stem}_{method.name.replace(' ', '_').lower()}.png"
            result_image.save(output_path)
            
            # Evaluate quality by checking transparency
            quality_score = evaluate_transparency(result_image)
            
            # Store results
            results.append({
                "image": image_path.name,
                "method": method.name,
                "execution_time": elapsed_time,
                "quality_score": quality_score,
                "output_path": output_path
            })
            
            logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}, Output: {output_path}")
    
    # Log summary
    if results:
        logger.info("\n=== RESULTS SUMMARY ===")
        
        # Group by method
        methods = set(r["method"] for r in results)
        
        for method in methods:
            method_results = [r for r in results if r["method"] == method]
            avg_time = sum(r["execution_time"] for r in method_results) / len(method_results)
            avg_quality = sum(r["quality_score"] for r in method_results) / len(method_results)
            
            logger.info(f"Method: {method}")
            logger.info(f"  Average Time: {avg_time:.2f}s")
            logger.info(f"  Average Quality: {avg_quality:.2f}")
    
    # Save results to report file
    save_results_report(results, output_dir)
    logger.info(f"Testing completed. Results saved to {output_dir}")


if __name__ == "__main__":
    # Run the tests
    include_carvekit = '--with-carvekit' in sys.argv
    test_all_methods_all_images(include_carvekit)
