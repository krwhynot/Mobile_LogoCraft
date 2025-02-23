import os
import sys
import cv2
import numpy as np

# Optional import for plotting (won't break if not available)
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# Add the project root to the Python path
project_root = r'R:\Projects\Python\Mobile_LogoCraft'
sys.path.insert(0, project_root)

class BackgroundRemovalAnalyzer:
    def __init__(self, image_path: str):
        """
        Initialize the analyzer with an input image
        
        Args:
            image_path (str): Path to the input image
        """
        # Read image
        self.original_image = cv2.imread(image_path)
        self.image_name = os.path.basename(image_path)
        
        if self.original_image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        self.original_image_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        
        # Convert to grayscale
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        
        # Metrics dictionary to store analysis results
        self.metrics = {}
    
    def analyze_thresholding(self):
        """
        Analyze image using Otsu's thresholding
        
        Returns:
            Dict of thresholding analysis metrics
        """
        # Otsu's Thresholding
        _, otsu_thresh = cv2.threshold(self.gray_image, 0, 255, 
                                       cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Calculate metrics
        background_ratio = np.sum(otsu_thresh == 0) / otsu_thresh.size
        foreground_ratio = np.sum(otsu_thresh == 255) / otsu_thresh.size
        
        return {
            'method': 'Otsu Thresholding',
            'otsu_threshold': cv2.threshold(self.gray_image, 0, 255, 
                                            cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0],
            'background_ratio': background_ratio,
            'foreground_ratio': foreground_ratio,
        }
    
    def analyze_edge_detection(self):
        """
        Analyze image using Canny edge detection
        
        Returns:
            Dict of edge detection analysis metrics
        """
        # Canny Edge Detection
        edges = cv2.Canny(self.gray_image, 100, 200)
        
        # Calculate edge metrics
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'method': 'Canny Edge Detection',
            'edge_density': edge_density,
            'total_edges': np.sum(edges > 0),
            'edge_percentage': edge_density * 100
        }
    
    def analyze_color_distribution(self):
        """
        Analyze color distribution in the image
        
        Returns:
            Dict of color analysis metrics
        """
        # Reshape image for color analysis
        pixels = self.original_image_rgb.reshape((-1, 3))
        
        # Calculate color statistics
        mean_color = np.mean(pixels, axis=0)
        std_color = np.std(pixels, axis=0)
        
        # Color diversity
        unique_colors = len(np.unique(pixels, axis=0))
        
        return {
            'method': 'Color Distribution',
            'mean_color_rgb': mean_color.tolist(),
            'color_std_dev_rgb': std_color.tolist(),
            'unique_color_count': unique_colors,
            'color_diversity_ratio': unique_colors / pixels.shape[0]
        }
    
    def analyze_contrast(self):
        """
        Analyze image contrast
        
        Returns:
            Dict of contrast analysis metrics
        """
        # Calculate image contrast
        contrast = np.std(self.gray_image)
        
        # Histogram analysis
        hist = cv2.calcHist([self.gray_image], [0], None, [256], [0, 256])
        hist_variance = np.var(hist)
        
        return {
            'method': 'Contrast Analysis',
            'contrast_std_dev': contrast,
            'histogram_variance': hist_variance,
            'min_intensity': np.min(self.gray_image),
            'max_intensity': np.max(self.gray_image)
        }
    
    def comprehensive_analysis(self):
        """
        Perform comprehensive analysis of image characteristics
        
        Returns:
            Dict of analysis results
        """
        # Run all analysis techniques
        self.metrics = {
            'thresholding': self.analyze_thresholding(),
            'edge_detection': self.analyze_edge_detection(),
            'color_distribution': self.analyze_color_distribution(),
            'contrast': self.analyze_contrast()
        }
        
        return self.metrics
    
    def recommend_background_removal_technique(self):
        """
        Recommend the best background removal technique
        
        Returns:
            str: Recommended technique
        """
        # Scoring criteria
        scores = {
            'Otsu Thresholding': 0,
            'GrabCut': 0,
            'K-Means Clustering': 0,
            'Deep Learning Segmentation': 0
        }
        
        # Thresholding score
        thresh_metrics = self.metrics['thresholding']
        if 0.3 < thresh_metrics['background_ratio'] < 0.7:
            scores['Otsu Thresholding'] += 2
        
        # Edge detection score
        edge_metrics = self.metrics['edge_detection']
        if 0.1 < edge_metrics['edge_density'] < 0.3:
            scores['GrabCut'] += 2
        
        # Color distribution score
        color_metrics = self.metrics['color_distribution']
        if 0.05 < color_metrics['color_diversity_ratio'] < 0.2:
            scores['K-Means Clustering'] += 2
        
        # Contrast score
        contrast_metrics = self.metrics['contrast']
        if contrast_metrics['contrast_std_dev'] > 30:
            scores['Deep Learning Segmentation'] += 2
        
        # Recommend technique with highest score
        recommended = max(scores, key=scores.get)
        
        return recommended

def batch_analyze_images(input_dir: str, output_dir: str):
    """
    Batch analyze images in a directory
    
    Args:
        input_dir (str): Directory containing input images
        output_dir (str): Directory to save analysis results
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a summary file
    summary_path = os.path.join(output_dir, 'background_removal_analysis_summary.txt')
    
    # Open summary file
    with open(summary_path, 'w') as summary_file:
        summary_file.write("Background Removal Technique Analysis\n")
        summary_file.write("=====================================\n\n")
        
        # Process each image in the input directory
        for filename in os.listdir(input_dir):
            # Check if file is an image
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                try:
                    # Full path to image
                    image_path = os.path.join(input_dir, filename)
                    
                    # Create analyzer
                    analyzer = BackgroundRemovalAnalyzer(image_path)
                    
                    # Perform analysis
                    results = analyzer.comprehensive_analysis()
                    
                    # Get recommended technique
                    recommended_technique = analyzer.recommend_background_removal_technique()
                    
                    # Write results to summary file
                    summary_file.write(f"Image: {filename}\n")
                    summary_file.write(f"Recommended Technique: {recommended_technique}\n\n")
                    
                    # Write detailed results
                    for technique, metrics in results.items():
                        summary_file.write(f"{technique.capitalize()} Metrics:\n")
                        for key, value in metrics.items():
                            summary_file.write(f"  {key}: {value}\n")
                        summary_file.write("\n")
                    
                    summary_file.write("-" * 50 + "\n\n")
                    
                    print(f"Analyzed: {filename}")
                
                except Exception as e:
                    summary_file.write(f"Error analyzing {filename}: {str(e)}\n\n")
                    print(f"Error analyzing {filename}: {str(e)}")
    
    print(f"Analysis complete. Results saved to {summary_path}")

def main():
    # Set input and output directories
    input_dir = r'R:\Projects\Python\Mobile_LogoCraft\tests\assets\test_images'
    output_dir = r'R:\Projects\Python\Mobile_LogoCraft\tests\assets\output'
    
    # Run batch analysis
    batch_analyze_images(input_dir, output_dir)

if __name__ == "__main__":
    main()