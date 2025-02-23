# Background Removal Technique Analyzer

## Overview
This script performs a comprehensive analysis of images to determine the most suitable background removal technique.

## Features
- Analyzes multiple images in a directory
- Provides metrics for:
  - Thresholding
  - Edge Detection
  - Color Distribution
  - Contrast Analysis
- Recommends best background removal technique
- Generates a detailed summary file

## Requirements
- Python 3.8+
- OpenCV
- NumPy
- Matplotlib

## Installation
```powershell
pip install opencv-python numpy matplotlib
```

## Usage
1. Set input directory to image folder
2. Set output directory for analysis results
3. Run the script

## Output
The script generates a `background_removal_analysis_summary.txt` file with:
- Image-specific analysis
- Recommended background removal technique
- Detailed metrics for each analysis method

## Recommended Techniques
- Otsu Thresholding
- GrabCut
- K-Means Clustering
- Deep Learning Segmentation

## Customization
- Modify scoring criteria
- Add new analysis techniques
- Adjust thresholds as needed

## Running the Test
Navigate to the project directory and run:
```powershell
python tests/batch_background_removal_analysis.py
```

## Troubleshooting
- Ensure all required libraries are installed
- Check input and output directory paths
- Verify image file formats
