import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.push_image_processor import PushIconProcessor

def process_all_test_images():
    # Setup paths
    test_images_dir = Path(r"R:\Projects\Python\Mobile_LogoCraft\tests\assets\test_images")
    output_dir = Path(r"R:\Projects\Python\Mobile_LogoCraft\tests\assets\output\push_icons")
    
    # Create processor
    processor = PushIconProcessor()
    
    # Process each image
    for image_path in test_images_dir.glob("*.png"):
        print(f"Processing {image_path.name}...")
        
        # Create output subdirectory for each image
        image_output_dir = output_dir / image_path.stem
        
        try:
            # Process with step-by-step output
            results = processor.process_step_by_step(str(image_path), str(image_output_dir))
            print(f"Successfully processed {image_path.name}")
            for step, path in results.items():
                print(f"  - {step}: {path}")
        except Exception as e:
            print(f"Error processing {image_path.name}: {e}")

if __name__ == "__main__":
    process_all_test_images()