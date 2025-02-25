import cv2
import numpy as np
from pathlib import Path
import os
import time

def remove_background_enhanced(input_path, output_path, method="combined"):
    """
    Remove image background using a combination of techniques.

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        method: Approach to use - options are:
                "contour" - Basic contour detection
                "threshold" - Otsu thresholding + contours
                "kmeans" - K-means clustering + contours
                "combined" - Best combination pipeline
    """
    # Read the image
    image = cv2.imread(input_path)
    if image is None:
        print(f"Error: Could not read image {input_path}")
        return False

    # Create a copy for results
    original = image.copy()

    # Convert to RGB for processing (OpenCV uses BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize if too large (speeds up processing)
    height, width = image.shape[:2]
    max_dimension = 1000
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height))
        image_rgb = cv2.resize(image_rgb, (new_width, new_height))
        print(f"Resized image to {new_width}x{new_height} for processing")

    # Create result mask
    mask = None

    # Method 1: Basic Contour Detection
    if method == "contour":
        mask = contour_method(image)

    # Method 2: Thresholding + Contours
    elif method == "threshold":
        mask = threshold_method(image)

    # Method 3: K-means + Contours
    elif method == "kmeans":
        mask = kmeans_method(image_rgb)

    # Method 4: Combined approach (best results)
    elif method == "combined":
        # Try thresholding first
        threshold_mask = threshold_method(image)

        # Try K-means as well
        kmeans_mask = kmeans_method(image_rgb)

        # Combine masks (take the union)
        mask = cv2.bitwise_or(threshold_mask, kmeans_mask)

        # Apply morphological operations to clean up
        mask = morphological_cleanup(mask)

        # Use contour detection as final refinement
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # If we found contours, refine the mask
        if contours:
            # Find the largest contour (assumed to be the main object)
            largest_contour = max(contours, key=cv2.contourArea)

            # Create a clean mask with just the largest contour
            refined_mask = np.zeros_like(mask)
            cv2.drawContours(refined_mask, [largest_contour], 0, 255, -1)

            # Apply morphological closing to fill holes
            refined_mask = cv2.morphologyEx(refined_mask, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

            mask = refined_mask

    # If no valid method was selected, use combined approach
    else:
        print(f"Warning: Unknown method '{method}', using combined approach")
        return remove_background_enhanced(input_path, output_path, "combined")

    # Resize mask back to original dimensions if needed
    if mask.shape[:2] != (height, width):
        mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)

    # Create transparent background image (RGBA)
    result = cv2.cvtColor(original, cv2.COLOR_BGR2BGRA)

    # Set alpha channel based on mask
    result[:, :, 3] = mask

    # Save the result
    cv2.imwrite(output_path, result)
    print(f"Saved background-removed image to {output_path}")

    return True

def contour_method(image):
    """Extract mask using contour detection"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges using Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Dilate edges to close gaps
    dilated = cv2.dilate(edges, None, iterations=2)

    # Find contours in the edge map
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create empty mask
    mask = np.zeros_like(gray)

    # If contours exist
    if contours:
        # Find largest contour (assuming it's the main object)
        largest_contour = max(contours, key=cv2.contourArea)

        # Draw filled contour on mask
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)

    return mask

def threshold_method(image):
    """Extract mask using Otsu's thresholding"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours from thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a clean mask
    mask = np.zeros_like(gray)

    # If contours exist, draw the largest one
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(mask, [largest_contour], 0, 255, -1)

    return mask

def kmeans_method(image_rgb):
    """Extract mask using K-means clustering"""
    # Reshape image for K-means
    pixels = image_rgb.reshape(-1, 3).astype(np.float32)

    # Define criteria and apply K-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    k = 3  # Number of clusters
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert back to uint8
    centers = np.uint8(centers)
    segmented_img = centers[labels.flatten()]
    segmented_img = segmented_img.reshape(image_rgb.shape)

    # Convert to grayscale and threshold to create mask
    gray = cv2.cvtColor(segmented_img, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return mask

def morphological_cleanup(mask):
    """Clean up the mask using morphological operations"""
    # Create kernel for morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Close small holes
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Open to remove small noise
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

    # Dilate slightly to ensure full coverage
    dilated = cv2.dilate(opened, kernel, iterations=1)

    return dilated

def process_directory(input_dir, output_dir, method="combined"):
    """Process all images in a directory"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get list of image files
    input_path = Path(input_dir)
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
    image_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]

    if not image_files:
        print(f"No image files found in {input_dir}")
        return

    print(f"Found {len(image_files)} images to process")

    # Process each image
    success_count = 0
    for i, input_file in enumerate(image_files, 1):
        output_file = Path(output_dir) / f"{input_file.stem}_nobg{input_file.suffix}"

        try:
            start_time = time.time()
            print(f"[{i}/{len(image_files)}] Processing: {input_file.name}...", end="", flush=True)

            if remove_background_enhanced(str(input_file), str(output_file), method):
                elapsed = time.time() - start_time
                print(f" Done! ({elapsed:.2f} seconds)")
                success_count += 1
            else:
                print(f" Failed!")

        except Exception as e:
            print(f" Error: {str(e)}")

    print(f"\nBackground removal complete! Successfully processed {success_count}/{len(image_files)} images.")
    print(f"Results saved in: {output_dir}")

if __name__ == "__main__":
    # Set directories
    base_dir = r"R:\Projects\Python\Mobile_LogoCraft"
    input_dir = os.path.join(base_dir, "tests", "assets", "test_images")
    output_dir = os.path.join(base_dir, "tests", "assets", "test_results")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found: {input_dir}")
        exit(1)

    print("Enhanced Background Removal Test")
    print("==============================")
    print(f"Input Directory: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print("==============================")

    # Choose processing method
    print("Available methods:")
    print("1. Contour detection only")
    print("2. Thresholding + Contours")
    print("3. K-means + Contours")
    print("4. Combined approach (recommended)")

    choice = input("Select method (1-4, default: 4): ").strip()

    method_map = {
        "1": "contour",
        "2": "threshold",
        "3": "kmeans",
        "4": "combined"
    }

    selected_method = method_map.get(choice, "combined")
    print(f"Using method: {selected_method}")

    # Start processing
    process_directory(input_dir, output_dir, selected_method)
