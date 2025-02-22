"""
Enhanced Background Removal for Push Notifications
"""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from rembg import remove
import logging
from .base import BaseImageProcessor

class PushProcessor(BaseImageProcessor):
    """Advanced processor for push notification icons with background removal."""

    def __init__(self, method="auto"):
        super().__init__()
        self.method = method

        # Edge detection parameters
        self.edge_params = {
            'gaussian_blur': (5, 5),
            'canny_threshold1': 30,
            'canny_threshold2': 100,
            'dilate_iterations': 2,
            'dilate_kernel': np.ones((3, 3), np.uint8)
        }

        # Color-based removal parameters
        self.color_params = {
            'tolerance': 30,  # Tolerance for background color
            'min_size': 100   # Min connected component size
        }

    def create_push_notification(self, input_path: Path, output_path: Path, size=None):
        """
        Create a push notification icon with background removal.
        
        Args:
            input_path (Path): Source image path
            output_path (Path): Output image path
            size (tuple): Optional custom size, defaults to FORMAT_CONFIGS["PUSH"]["size"]
        """
        try:
            self.validate_input(input_path, output_path)
            push_config = self.get_format_config("PUSH")
            size = size or push_config["size"]

            with Image.open(input_path) as img:
                img = self._preprocess_image(img)

                # Apply background removal
                if self.method == "auto":
                    img = self._auto_remove_background(img)
                elif self.method == "ai":
                    img = self.make_transparent_ai(img)
                elif self.method == "edge":
                    img = self.make_transparent_edges(img)
                elif self.method == "color":
                    img = self.make_transparent_color(img)
                elif self.method == "hybrid":
                    img = self._hybrid_remove_background(img)

                # Final processing & save
                img = self._postprocess_image(img, size)
                img.save(output_path, format="PNG", 
                        optimize=push_config["optimize"],
                        quality=push_config["quality"])

        except Exception as e:
            self.logger.error(f"Error processing push notification: {str(e)}")
            raise

    def _preprocess_image(self, image):
        """Prepares image by enhancing contrast & reducing noise."""
        image = image.convert("RGBA")
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)

        # Denoise while preserving edges
        denoised = cv2.bilateralFilter(cv_image, 9, 75, 75)

        # Enhance contrast
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGRA2LAB)
        lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lab[:, :, 0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGRA)

        return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGRA2RGBA))

    def _auto_remove_background(self, image):
        """Choose best method dynamically based on image complexity."""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        try:
            return self.make_transparent_ai(image) if edge_density > 0.1 else self.make_transparent_color(image)
        except Exception:
            return self.make_transparent_edges(image)

    def make_transparent_color(self, image):
        """Remove background based on color similarity."""
        data = np.array(image)
        background = data[0, 0, :3]  # Assume top-left corner is background
        mask = np.all(np.abs(data[:, :, :3] - background) <= self.color_params['tolerance'], axis=2)

        # Remove small noise components
        num_labels, labels = cv2.connectedComponents(mask.astype(np.uint8))
        for i in range(1, num_labels):
            if np.sum(labels == i) < self.color_params['min_size']:
                mask[labels == i] = False

        data[mask, 3] = 0
        return Image.fromarray(data)

    def make_transparent_edges(self, image):
        """Remove background using edge detection & smooth inpainting."""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, self.edge_params['gaussian_blur'], 0)

        edges = cv2.Canny(blurred, self.edge_params['canny_threshold1'], self.edge_params['canny_threshold2'])
        mask = cv2.dilate(edges, self.edge_params['dilate_kernel'], iterations=self.edge_params['dilate_iterations'])

        # Smooth mask using inpainting
        inpainted = cv2.inpaint(cv_image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        result = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGBA)
        result[:, :, 3] = 255 - mask  # Make edges transparent

        return Image.fromarray(result)

    def make_transparent_ai(self, image):
        """Remove background using AI & enhance alpha channel."""
        no_bg = remove(image)
        data = np.array(no_bg)
        alpha = cv2.GaussianBlur(data[:, :, 3], (3, 3), 0)
        data[:, :, 3] = cv2.normalize(alpha, None, 0, 255, cv2.NORM_MINMAX)
        return Image.fromarray(data)

    def _postprocess_image(self, img, size):
        """Scale and center the image."""
        # Resize to target size
        img = img.resize(size, Image.LANCZOS)
        # Center the image if needed
        if img.size != size:
            new_img = Image.new('RGBA', size, (0, 0, 0, 0))
            paste_x = (size[0] - img.size[0]) // 2
            paste_y = (size[1] - img.size[1]) // 2
            new_img.paste(img, (paste_x, paste_y))
            img = new_img
        return img