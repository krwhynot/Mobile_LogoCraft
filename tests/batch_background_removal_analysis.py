"""
Batch analysis script for evaluating background removal methods with different parameters
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import test module functionality
from test_background_removal import (
    ThresholdRemovalMethod, 
    ChromaKeyRemovalMethod,
    ContourBasedRemovalMethod,
    GrabCutRemovalMethod,
    evaluate_transparency,
    save_results_report
)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Batch Background Removal Analysis')
    
    parser.add_argument('--input-dir', type=str, 
                        default=str(Path(__file__).parent / 'assets' / 'test_images'),
                        help='Directory containing test images')
    
    parser.add_argument('--output-dir', type=str, 
                        default=str(Path(__file__).parent / 'assets' / 'output' / 'background_removal_batch'),
                        help='Directory for output files')
    
    parser.add_argument('--methods', type=str, nargs='+',
                        choices=['threshold', 'chroma_key', 'contour', 'grabcut', 'all'],
                        default=['all'],
                        help='Methods to test')
    
    parser.add_argument('--threshold-values', type=int, nargs='+',
                        default=[220, 230, 240, 250],
                        help='Threshold values to test for threshold method')
    
    parser.add_argument('--tolerance-values', type=int, nargs='+',
                        default=[10, 20, 30, 40],
                        help='Tolerance values to test for chroma key method')
    
    parser.add_argument('--blur-sizes', type=int, nargs='+',
                        default=[3, 5, 7],
                        help='Blur sizes to test for contour method')
    
    parser.add_argument('--grabcut-iterations', type=int, nargs='+',
                        default=[3, 5, 7],
                        help='Iteration counts to test for GrabCut method')
    
    parser.add_argument('--extensions', type=str, nargs='+',
                        default=['.png', '.jpg', '.jpeg'],
                        help='File extensions to process')
    
    return parser.parse_args()


def run_batch_analysis(args):
    """Run batch analysis with different parameters"""
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get test images
    image_files = []
    for ext in args.extensions:
        image_files.extend(list(input_dir.glob(f'*{ext}')))
    
    if not image_files:
        logger.error(f"No images found in {input_dir} with extensions {args.extensions}")
        return
    
    logger.info(f"Found {len(image_files)} images for processing")
    
    # Determine which methods to test
    methods_to_test = args.methods
    if 'all' in methods_to_test:
        methods_to_test = ['threshold', 'chroma_key', 'contour', 'grabcut']
    
    # Initialize results
    results = []
    
    # Process each image
    for image_path in image_files:
        image_name = image_path.name
        logger.info(f"Processing image: {image_name}")
        
        # Load image
        try:
            from PIL import Image
            image = Image.open(image_path)
            
            # Create directory for this image's results
            image_output_dir = output_dir / image_path.stem
            os.makedirs(image_output_dir, exist_ok=True)
            
            # Test each method with different parameters
            if 'threshold' in methods_to_test:
                for threshold in args.threshold_values:
                    for tolerance in args.tolerance_values:
                        method = ThresholdRemovalMethod(threshold=threshold, tolerance=tolerance)
                        method_name = f"Threshold_{threshold}_{tolerance}"
                        logger.info(f"  Testing {method_name}")
                        
                        start_time = time.time()
                        result_image = method.remove_background(image)
                        elapsed_time = time.time() - start_time
                        
                        # Save result
                        output_path = image_output_dir / f"{method_name}.png"
                        result_image.save(output_path)
                        
                        # Evaluate quality
                        quality_score = evaluate_transparency(result_image)
                        
                        # Store result
                        results.append({
                            "image": image_name,
                            "method": method_name,
                            "execution_time": elapsed_time,
                            "quality_score": quality_score,
                            "output_path": output_path,
                            "parameters": {
                                "threshold": threshold,
                                "tolerance": tolerance
                            }
                        })
                        
                        logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}")
            
            if 'chroma_key' in methods_to_test:
                for tolerance in args.tolerance_values:
                    method = ChromaKeyRemovalMethod(target_color=(255, 255, 255), tolerance=tolerance)
                    method_name = f"ChromaKey_{tolerance}"
                    logger.info(f"  Testing {method_name}")
                    
                    start_time = time.time()
                    result_image = method.remove_background(image)
                    elapsed_time = time.time() - start_time
                    
                    # Save result
                    output_path = image_output_dir / f"{method_name}.png"
                    result_image.save(output_path)
                    
                    # Evaluate quality
                    quality_score = evaluate_transparency(result_image)
                    
                    # Store result
                    results.append({
                        "image": image_name,
                        "method": method_name,
                        "execution_time": elapsed_time,
                        "quality_score": quality_score,
                        "output_path": output_path,
                        "parameters": {
                            "tolerance": tolerance
                        }
                    })
                    
                    logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}")
            
            if 'contour' in methods_to_test:
                for threshold in args.threshold_values:
                    for blur_size in args.blur_sizes:
                        method = ContourBasedRemovalMethod(threshold=threshold, blur_size=blur_size)
                        method_name = f"Contour_{threshold}_{blur_size}"
                        logger.info(f"  Testing {method_name}")
                        
                        start_time = time.time()
                        result_image = method.remove_background(image)
                        elapsed_time = time.time() - start_time
                        
                        # Save result
                        output_path = image_output_dir / f"{method_name}.png"
                        result_image.save(output_path)
                        
                        # Evaluate quality
                        quality_score = evaluate_transparency(result_image)
                        
                        # Store result
                        results.append({
                            "image": image_name,
                            "method": method_name,
                            "execution_time": elapsed_time,
                            "quality_score": quality_score,
                            "output_path": output_path,
                            "parameters": {
                                "threshold": threshold,
                                "blur_size": blur_size
                            }
                        })
                        
                        logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}")
            
            if 'grabcut' in methods_to_test:
                for iterations in args.grabcut_iterations:
                    method = GrabCutRemovalMethod(iterations=iterations)
                    method_name = f"GrabCut_{iterations}"
                    logger.info(f"  Testing {method_name}")
                    
                    start_time = time.time()
                    result_image = method.remove_background(image)
                    elapsed_time = time.time() - start_time
                    
                    # Save result
                    output_path = image_output_dir / f"{method_name}.png"
                    result_image.save(output_path)
                    
                    # Evaluate quality
                    quality_score = evaluate_transparency(result_image)
                    
                    # Store result
                    results.append({
                        "image": image_name,
                        "method": method_name,
                        "execution_time": elapsed_time,
                        "quality_score": quality_score,
                        "output_path": output_path,
                        "parameters": {
                            "iterations": iterations
                        }
                    })
                    
                    logger.info(f"    Time: {elapsed_time:.2f}s, Quality: {quality_score:.2f}")
                    
        except Exception as e:
            logger.error(f"Error processing {image_name}: {e}")
            continue
    
    # Generate enhanced report
    generate_enhanced_report(results, output_dir)
    logger.info(f"Batch analysis complete. Report saved to {output_dir / 'batch_analysis_report.md'}")


def generate_enhanced_report(results: List[Dict], output_dir: Path):
    """Generate an enhanced report with parameter analysis"""
    report_path = output_dir / "batch_analysis_report.md"
    
    with open(report_path, 'w') as f:
        f.write("# Background Removal Batch Analysis Report\n\n")
        f.write(f"Analysis date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Executive Summary\n\n")
        
        # Find best methods overall
        best_quality_result = max(results, key=lambda r: r["quality_score"])
        fastest_result = min(results, key=lambda r: r["execution_time"])
        
        f.write(f"- **Best Quality Method:** {best_quality_result['method']} (Score: {best_quality_result['quality_score']:.3f})\n")
        f.write(f"- **Fastest Method:** {fastest_result['method']} (Time: {fastest_result['execution_time']:.3f}s)\n\n")
        
        # Aggregate results by method type
        method_types = {}
        for result in results:
            method_type = result["method"].split("_")[0]
            if method_type not in method_types:
                method_types[method_type] = []
            method_types[method_type].append(result)
        
        # Best configurations by method type
        f.write("### Best Configurations by Method\n\n")
        for method_type, method_results in method_types.items():
            best_result = max(method_results, key=lambda r: r["quality_score"])
            f.write(f"**{method_type}:**\n")
            f.write(f"- Parameters: {best_result['parameters']}\n")
            f.write(f"- Quality Score: {best_result['quality_score']:.3f}\n")
            f.write(f"- Execution Time: {best_result['execution_time']:.3f}s\n\n")
        
        # Parameter analysis
        f.write("## Parameter Analysis\n\n")
        
        # Threshold analysis
        if "Threshold" in method_types:
            threshold_results = method_types["Threshold"]
            f.write("### Threshold Parameter Analysis\n\n")
            
            # Group by threshold value
            threshold_groups = {}
            for result in threshold_results:
                threshold = result["parameters"]["threshold"]
                if threshold not in threshold_groups:
                    threshold_groups[threshold] = []
                threshold_groups[threshold].append(result)
            
            # Average performance by threshold
            f.write("#### Effect of Threshold Value\n\n")
            f.write("| Threshold | Avg Quality | Avg Time (s) |\n")
            f.write("|-----------|-------------|-------------|\n")
            
            for threshold, group in sorted(threshold_groups.items()):
                avg_quality = sum(r["quality_score"] for r in group) / len(group)
                avg_time = sum(r["execution_time"] for r in group) / len(group)
                f.write(f"| {threshold} | {avg_quality:.3f} | {avg_time:.3f} |\n")
            
            f.write("\n")
            
            # Group by tolerance
            tolerance_groups = {}
            for result in threshold_results:
                tolerance = result["parameters"]["tolerance"]
                if tolerance not in tolerance_groups:
                    tolerance_groups[tolerance] = []
                tolerance_groups[tolerance].append(result)
            
            # Average performance by tolerance
            f.write("#### Effect of Tolerance Value\n\n")
            f.write("| Tolerance | Avg Quality | Avg Time (s) |\n")
            f.write("|-----------|-------------|-------------|\n")
            
            for tolerance, group in sorted(tolerance_groups.items()):
                avg_quality = sum(r["quality_score"] for r in group) / len(group)
                avg_time = sum(r["execution_time"] for r in group) / len(group)
                f.write(f"| {tolerance} | {avg_quality:.3f} | {avg_time:.3f} |\n")
            
            f.write("\n")
        
        # Image-specific analysis
        f.write("## Image-Specific Analysis\n\n")
        
        images = set(r["image"] for r in results)
        for image in sorted(images):
            image_results = [r for r in results if r["image"] == image]
            best_result = max(image_results, key=lambda r: r["quality_score"])
            
            f.write(f"### {image}\n\n")
            f.write(f"- **Best Method:** {best_result['method']}\n")
            f.write(f"- **Quality Score:** {best_result['quality_score']:.3f}\n")
            f.write(f"- **Execution Time:** {best_result['execution_time']:.3f}s\n")
            f.write(f"- **Parameters:** {best_result['parameters']}\n\n")
            
            # Top 3 methods for this image
            f.write("#### Top 3 Methods\n\n")
            f.write("| Method | Quality | Time (s) | Parameters |\n")
            f.write("|--------|---------|----------|------------|\n")
            
            sorted_results = sorted(image_results, key=lambda r: r["quality_score"], reverse=True)[:3]
            for result in sorted_results:
                params_str = ", ".join(f"{k}={v}" for k, v in result["parameters"].items())
                f.write(f"| {result['method']} | {result['quality_score']:.3f} | {result['execution_time']:.3f} | {params_str} |\n")
            
            f.write("\n")
        
        # Overall results table
        f.write("## Complete Results\n\n")
        f.write("| Image | Method | Quality | Time (s) | Parameters |\n")
        f.write("|-------|--------|---------|----------|------------|\n")
        
        # Sort by image name and then by quality score (descending)
        sorted_results = sorted(results, key=lambda r: (r["image"], -r["quality_score"]))
        
        for result in sorted_results:
            params_str = ", ".join(f"{k}={v}" for k, v in result["parameters"].items())
            f.write(f"| {result['image']} | {result['method']} | {result['quality_score']:.3f} | {result['execution_time']:.3f} | {params_str} |\n")


if __name__ == "__main__":
    args = parse_args()
    run_batch_analysis(args)
