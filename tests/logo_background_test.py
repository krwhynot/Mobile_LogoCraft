"""
Logo Background Removal Test Script
----------------------------------
Uses contour detection as the primary method with additional cleanup from other methods
to produce the best possible background removal for logos.
"""

import os
import sys
import time
import cv2
import numpy as np
from pathlib import Path
import argparse

def optimize_background_removal(image):
    """
    Remove background using contour method as primary approach
    with additional refinement from other methods.
    """
    # Step 1: Contour-based extraction (primary method)
    contour_mask = contour_method(image)
    
    # Step 2: Use thresholding for additional mask refinement
    threshold_mask = threshold_method(image)
    
    # Step 3: Combine masks to get best coverage
    combined_mask = cv2.bitwise_or(contour_mask, threshold_mask)
    
    # Step 4: Clean up with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    
    # Step 5: Find contours in the combined mask for final refinement
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Use all significant contours, not just the largest one
    refined_mask = np.zeros_like(combined_mask)
    for contour in contours:
        # Filter out tiny contours (noise)
        if cv2.contourArea(contour) > 100:  # Adjust threshold as needed
            cv2.drawContours(refined_mask, [contour], 0, 255, -1)
    
    # Final cleanup to fill any small holes
    refined_mask = cv2.morphologyEx(refined_mask, cv2.MORPH_CLOSE, kernel)
    
    return refined_mask

def contour_method(image):
    """Extract mask using contour detection (primary method)"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect edges using Canny (with slightly more sensitive parameters)
    edges = cv2.Canny(blurred, 30, 150)
    
    # Dilate edges to close gaps
    dilated = cv2.dilate(edges, None, iterations=2)
    
    # Find contours in the edge map
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create empty mask
    mask = np.zeros_like(gray)
    
    # Draw all significant contours, not just the largest
    for contour in contours:
        # Filter out tiny contours (noise)
        if cv2.contourArea(contour) > 50:
            cv2.drawContours(mask, [contour], -1, 255, -1)
    
    return mask

def threshold_method(image):
    """Extract mask using Otsu's thresholding (secondary method for cleanup)"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    return thresh

def create_transparent_output(image, mask):
    """Create a transparent PNG from the original image and mask"""
    # Create RGBA image (with alpha channel)
    rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    
    # Set alpha channel based on mask
    rgba[:, :, 3] = mask
    
    return rgba

def process_logo(image_path, output_dir):
    """Process the logo with the optimized background removal approach"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return False
    
    # Get base filename
    base_name = os.path.basename(image_path).split('.')[0]
    
    # Process with optimized method
    print(f"Processing logo with optimized contour-based method...")
    start_time = time.time()
    
    # Run the optimized background removal
    mask = optimize_background_removal(image)
    transparent = create_transparent_output(image, mask)
    
    processing_time = time.time() - start_time
    
    # Save result
    output_path = os.path.join(output_dir, f"{base_name}_nobg.png")
    cv2.imwrite(output_path, transparent)
    
    # Calculate percentage of retained pixels
    retained_pixels = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1]) * 100
    
    print(f"Background removal complete:")
    print(f"  - Processing time: {processing_time:.2f} seconds")
    print(f"  - Retained {retained_pixels:.1f}% of pixels")
    print(f"  - Result saved to: {output_path}")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove background from a logo using contour-based method")
    parser.add_argument("--image", help="Path to logo image (default: hungry_howies_logo.png in assets directory)")
    parser.add_argument("--output", help="Output directory (default: test_results/logo_test)")
    
    args = parser.parse_args()
    
    # Default paths
    base_dir = r"R:\Projects\Python\Mobile_LogoCraft"
    image_path = args.image or os.path.join(base_dir, "tests", "assets", "hungry_howies_logo.png")
    output_dir = args.output or os.path.join(base_dir, "tests", "results", "logo_test")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
    
    # Run background removal
    print(f"Processing logo: {image_path}")
    process_logo(image_path, output_dir)
