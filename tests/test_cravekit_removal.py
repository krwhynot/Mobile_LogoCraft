"""
Test file for evaluating CraveKit background removal method.
This implements the CarveKit library (OPHoperHPO/image-background-remove-tool) for
high-quality background removal using neural networks.
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

import numpy as np
from PIL import Image
import pytest

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

# Import test utilities from background_removal test
from test_background_removal import evaluate_transparency, save_results_report

# Check if carvekit is installed
try:
    import torch
    from carvekit.api.high import HiInterface
    CARVEKIT_AVAILABLE = True
except ImportError:
    CARVEKIT_AVAILABLE = False
    logger.warning("CarveKit library not found. Please install with: pip install carvekit")


class CraveKitRemovalMethod:
    """Remove background using CraveKit (image-background-remove-tool)"""
    
    def __init__(
        self, 
        model_type: str = "tracer_b7",  # or "u2net", "basnet", "deeplabv3"
        object_type: str = "object",    # or "hairs-like"
        fp16: bool = False,
        device: str = "cpu",
        seg_mask_size: int = 640,       # Use 640 for Tracer B7 and 320 for U2Net
        matting_mask_size: int = 2048,
        trimap_dilation: int = 30,
        trimap_erosion_iters: int = 5,
        trimap_prob_threshold: int = 231,
        batch_size_seg: int = 1,
        batch_size_matting: int = 1
    ):
        """
        Initialize CraveKit background removal method.
        
        Args:
            model_type: Neural network model to use (tracer_b7, u2net, basnet, deeplabv3)
            object_type: Type of objects to process (object, hairs-like)
            fp16: Use mixed precision (FP16) for faster processing
            device: Processing device (cpu, cuda)
            seg_mask_size: Size of segmentation mask (640 for tracer_b7, 320 for others)
            matting_mask_size: Size of matting mask
            trimap_dilation: Dilation amount for trimap generation
            trimap_erosion_iters: Erosion iterations for trimap generation
            trimap_prob_threshold: Probability threshold for trimap
            batch_size_seg: Batch size for segmentation
            batch_size_matting: Batch size for matting
        
        Raises:
            ImportError: If CarveKit library is not available
        """
        super().__init__()
        self.name = f"CraveKit_{model_type}"
        self.description = f"Background removal using CarveKit with {model_type} neural network"
        
        if not CARVEKIT_AVAILABLE:
            raise ImportError("CarveKit library not available. Please install with: pip install carvekit")
        
        self.model_type = model_type
        self.object_type = object_type
        self.fp16 = fp16
        self.device = device
        self.seg_mask_size = seg_mask_size
        self.matting_mask_size = matting_mask_size
        self.trimap_dilation = trimap_dilation
        self.trimap_erosion_iters = trimap_erosion_iters
        self.trimap_prob_threshold = trimap_prob_threshold
        self.batch_size_seg = batch_size_seg
        self.batch_size_matting = batch_size_matting
        
        self._interface = None
    
    @property
    def interface(self):
        """Lazy initialization of HiInterface to avoid loading models until needed"""
        if self._interface is None:
            self._interface = HiInterface(
                object_type=self.object_type,
                batch_size_seg=self.batch_size_seg,
                batch_size_matting=self.batch_size_matting,
                device=self.device,
                seg_mask_size=self.seg_mask_size,
                matting_mask_size=self.matting_mask_size,
                trimap_prob_threshold=self.trimap_prob_threshold,
                trimap_dilation=self.trimap_dilation,
                trimap_erosion_iters=self.trimap_erosion_iters,
                fp16=self.fp16
            )
        return self._interface
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove background using CarveKit.
        
        Args:
            image: Input PIL image
            
        Returns:
            PIL image with background removed
        """
        # Convert image to RGB if in RGBA to standardize input
        if image.mode == 'RGBA':
            # Create white background
            background = Image.new('RGBA', image.size, (255, 255, 255, 255))
            # Composite the image with white background
            image = Image.alpha_composite(background, image).convert('RGB')
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save image to temporary file
        temp_dir = Path(__file__).parent / 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = temp_dir / 'temp_input.jpg'
        image.save(temp_path)
        
        try:
            # Process using CarveKit
            result_images = self.interface([str(temp_path)])
            result_image = result_images[0]
            
            # Clean up temporary file
            os.remove(temp_path)
            
            return result_image
        
        except Exception as e:
            logger.error(f"Error in CarveKit processing: {e}")
            # Clean up temporary file
            if temp_path.exists():
                os.remove(temp_path)
            
            # Return original image with alpha channel
            return image.convert('RGBA')
    
    def get_info(self) -> Dict:
        """Return information about this method"""
        return {
            "name": self.name,
            "description": self.description,
            "model_type": self.model_type,
            "object_type": self.object_type,
            "device": self.device,
            "seg_mask_size": self.seg_mask_size,
            "matting_mask_size": self.matting_mask_size
        }


def get_method_pros_cons(method_name: str) -> Tuple[List[str], List[str]]:
    """
    Get pros and cons for CraveKit methods
    Returns: (pros, cons)
    """
    if "CraveKit" not in method_name:
        return [], []
    
    model_type = method_name.split("_")[1] if "_" in method_name else "tracer_b7"
    
    pros_cons = {
        "tracer_b7": (
            [
                "State-of-the-art segmentation accuracy (90% F1-Score)",
                "Excellent for general objects and scenes",
                "Better detail preservation than other models",
                "Highly optimized inference speed",
                "Advanced matting algorithm for fine details"
            ],
            [
                "Higher memory requirements than other models",
                "Requires external dependency installation",
                "May struggle with extremely fine details like hairs",
                "Slower than basic thresholding methods",
                "Requires larger input resolution for best results"
            ]
        ),
        "u2net": (
            [
                "Specialized for hair and fine details",
                "Good balance of quality and processing time",
                "Excellent for human subjects",
                "Handles complex edges well",
                "Widely tested on diverse images"
            ],
            [
                "Lower overall accuracy than Tracer B7 (80.4% F1-Score)",
                "Can produce artifacts on non-human subjects",
                "Requires careful parameter tuning",
                "Neural network dependency increases complexity",
                "Performance varies based on image content"
            ]
        ),
        "basnet": (
            [
                "Good general-purpose segmentation",
                "Effective for objects with clear boundaries",
                "Consistent performance across various domains",
                "Faster than GrabCut with similar quality",
                "Integrated matting improves edge quality"
            ],
            [
                "Lower accuracy than Tracer B7 (80.3% F1-Score)",
                "Less effective for fine details than U2Net",
                "Can produce overly smooth boundaries",
                "Requires separate post-processing for best results",
                "Higher resource usage than basic methods"
            ]
        ),
        "deeplabv3": (
            [
                "Fast inference time",
                "Good for common objects (people, animals, cars)",
                "Lower memory requirements than other models",
                "Works well with clearly defined objects",
                "Strong semantic understanding"
            ],
            [
                "Lower accuracy than other models (67.4% IoU)",
                "Struggles with unusual or complex objects",
                "Less precise boundaries than specialized models",
                "Requires larger trimap parameters for best results",
                "Not optimal for fine details like hair"
            ]
        )
    }
    
    return pros_cons.get(model_type, ([], []))


@pytest.mark.skipif(not CARVEKIT_AVAILABLE, reason="CarveKit library not installed")
def test_carvekit_methods():
    """Test CarveKit background removal methods"""
    # Set paths
    test_dir = Path(__file__).parent
    test_images_dir = test_dir / 'assets' / 'test_images'
    output_dir = test_dir / 'assets' / 'output' / 'carvekit_removal'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define test methods based on available GPU
    if torch.cuda.is_available():
        device = 'cuda'
        logger.info("CUDA available, using GPU for processing")
    else:
        device = 'cpu'
        logger.info("CUDA not available, using CPU for processing")
    
    # Define methods to test based on available device
    methods = [
        CraveKitRemovalMethod(model_type="tracer_b7", device=device, 
                              seg_mask_size=640, trimap_dilation=30, trimap_erosion_iters=5),
        CraveKitRemovalMethod(model_type="u2net", device=device, 
                              seg_mask_size=320, trimap_dilation=30, trimap_erosion_iters=5),
    ]
    
    # For CUDA devices with sufficient memory, add more methods
    if device == 'cuda' and torch.cuda.get_device_properties(0).total_memory > 8 * 1024 * 1024 * 1024:
        methods.extend([
            CraveKitRemovalMethod(model_type="basnet", device=device, 
                                  seg_mask_size=320, trimap_dilation=30, trimap_erosion_iters=5),
            CraveKitRemovalMethod(model_type="deeplabv3", device=device, 
                                  seg_mask_size=1024, trimap_dilation=40, trimap_erosion_iters=20),
        ])
    
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
            try:
                result_image = method.remove_background(image)
                elapsed_time = time.time() - start_time
                
                # Save result
                output_path = output_dir / f"{image_path.stem}_{method.name}.png"
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
                
                logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}")
            
            except Exception as e:
                logger.error(f"Error processing {image_path.name} with {method.name}: {e}")
    
    # Log summary
    if results:
        logger.info("\n=== RESULTS SUMMARY ===")
        
        # Group by method
        method_names = set(r["method"] for r in results)
        
        for method_name in method_names:
            method_results = [r for r in results if r["method"] == method_name]
            avg_time = sum(r["execution_time"] for r in method_results) / len(method_results)
            avg_quality = sum(r["quality_score"] for r in method_results) / len(method_results)
            
            logger.info(f"Method: {method_name}")
            logger.info(f"  Average Time: {avg_time:.2f}s")
            logger.info(f"  Average Quality: {avg_quality:.2f}")
    
    # Save results to report file
    save_results_report(results, output_dir)
    logger.info(f"Testing completed. Results saved to {output_dir}")


if __name__ == "__main__":
    # Run the tests if CarveKit is available
    if CARVEKIT_AVAILABLE:
        test_carvekit_methods()
    else:
        logger.error("CarveKit library not available. Please install with: pip install carvekit")
