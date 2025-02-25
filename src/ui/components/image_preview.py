"""
Image preview component for the Mobile LogoCraft application.
Displays a preview of the currently selected image, adapting to the image's dimensions.
"""
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, QSize, Signal
from pathlib import Path
import os
import logging

from ..theme.colors import HungerRushColors, ThemeStyles, ThemeMode

logger = logging.getLogger(__name__)

class ImagePreview(QFrame):
    """
    A component that displays a preview of the selected image.
    """
    # Signal to emit when a file is dropped
    fileDropped = Signal(str)
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """
        Initialize the image preview component.
        
        Args:
            theme_mode: The theme mode (light/dark) to apply.
        """
        super().__init__()
        self.theme_mode = theme_mode
        self.preview_image = None
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Apply styles based on theme
        self._apply_theme()
        
        # Set up the UI
        self._setup_ui()
        
        # Show placeholder by default
        self.show_placeholder()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create the image label with proportional sizing
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(200, 200)
        
        # Add the label to the layout
        layout.addWidget(self.image_label, 0, Qt.AlignCenter)
    
    def _apply_theme(self):
        """Apply theme styling to the component."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        
        self.setStyleSheet(f"""
            ImagePreview {{
                background-color: {colors['section_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['md']};
            }}
            
            QLabel {{
                color: {colors['label_color']};
                background-color: {colors['bg_color']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['md']};
                border: 1px dashed {colors['border_color']};
            }}
        """)
    
    def show_placeholder(self):
        """Show a placeholder message when no image is selected."""
        self.image_label.setPixmap(QPixmap())  # Clear pixmap
        self.image_label.setText("Drop your image here\nor click Browse")
        self.preview_image = None
    
    def update_preview(self, image_path: str):
        """
        Update the preview with the selected image.
        
        Args:
            image_path: Path to the image file.
        """
        try:
            # Check if the path exists
            if not Path(image_path).exists():
                self.show_placeholder()
                return
            
            # Load the image using QImage for better error handling
            image = QImage(image_path)
            if image.isNull():
                logger.error(f"Failed to load image: {image_path}")
                self.show_placeholder()
                return
            
            # Get the original dimensions
            original_width = image.width()
            original_height = image.height()
            
            # Get available size for preview (accounting for padding)
            available_width = self.width() - 30  # 15px padding on each side
            available_height = self.height() - 30
            
            # Calculate scale factor to fit within available space
            scale_factor = min(
                1.0,  # Don't upscale
                available_width / original_width,
                available_height / original_height
            )
            
            # Calculate new dimensions
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Convert to QPixmap and scale it
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(
                QSize(new_width, new_height),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Update the image label
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")  # Clear any text
            
            # Store the current preview image
            self.preview_image = image_path
            
        except Exception as e:
            logger.error(f"Error updating preview: {str(e)}")
            self.show_placeholder()
    
    def clear_preview(self):
        """Clear the current preview."""
        self.show_placeholder()
    
    def resizeEvent(self, event):
        """Handle resize events to update the image preview."""
        super().resizeEvent(event)
        if self.preview_image:
            self.update_preview(self.preview_image)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events, accepting only valid file drops."""
        if event.mimeData().hasUrls():
            # Check if at least one URL is a valid image file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self._is_valid_image(file_path):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Process the dropped file and emit signal."""
        file_path = event.mimeData().urls()[0].toLocalFile()
        if self._is_valid_image(file_path):
            # Emit signal with the file path
            self.fileDropped.emit(file_path)
            event.accept()
        else:
            event.ignore()
    
    def _is_valid_image(self, file_path: str) -> bool:
        """
        Check if the file has a valid image extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if the file has a valid image extension
        """
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.jfif'}
        return os.path.splitext(file_path)[1].lower() in valid_extensions
