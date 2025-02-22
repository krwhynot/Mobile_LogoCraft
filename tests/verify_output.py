from PIL import Image
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_alpha_distribution(img_path: Path):
    """Analyze alpha channel distribution of an image."""
    with Image.open(img_path) as img:
        if img.mode != 'RGBA':
            logging.warning(f"{img_path} is not in RGBA mode")
            return
        
        _, _, _, alpha = img.split()
        alpha_array = np.array(alpha)
        
        # Get unique alpha values and their counts
        unique, counts = np.unique(alpha_array, return_counts=True)
        total_pixels = alpha_array.size
        
        logging.info(f"\nAnalysis for {img_path.name}:")
        logging.info(f"Image size: {img.size}")
        logging.info("\nAlpha value distribution:")
        for value, count in zip(unique, counts):
            percentage = (count / total_pixels) * 100
            logging.info(f"Alpha {value}: {count} pixels ({percentage:.2f}%)")

def verify_dimensions(img_path: Path):
    """Verify image dimensions are correct."""
    with Image.open(img_path) as img:
        width, height = img.size
        if width != 96 or height != 96:
            logging.error(f"Invalid dimensions: {width}x{height} (expected 96x96)")
        else:
            logging.info("Dimensions: OK (96x96)")

def main():
    output_dir = Path("tests/assets/output/push_icons")
    test_file = output_dir / "test_output.png"
    
    if not test_file.exists():
        logging.error(f"Output file not found: {test_file}")
        return
    
    verify_dimensions(test_file)
    analyze_alpha_distribution(test_file)

if __name__ == "__main__":
    main()