"""
Specialized drop zone component for handling image file drops in the HungerRush Image Processing Application.
Provides visual feedback and handles drag-and-drop events for image files.
"""
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os

from ..theme.colors import HungerRushColors, ThemeStyles, ThemeMode

class ImageDropZone(QLabel):
    """A customized drop zone for image files with HungerRush styling."""
    
    # Signal emitted when a file is dropped, passing the file path
    fileDropped = Signal(str)
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK, parent=None):
        """
        Initialize the drop zone with appropriate styling and event handling.
        
        Args:
            theme_mode: The theme mode (light/dark) to apply
            parent: Parent widget
        """
        super().__init__(parent)
        self.theme_mode = theme_mode
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drop image here or click Browse")
        self._apply_style()
    
    def _apply_style(self):
        """Apply HungerRush theme styling to the drop zone."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {colors['label_color']};
                background-color: {colors['section_bg']};
                border: 2px dashed {colors['border_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['lg']};
                padding: {ThemeStyles.SPACING['xl']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['md']};
            }}
            
            QLabel:hover {{
                background-color: {colors['section_bg']};
                border-color: {colors['button_color']};
            }}
        """)
    
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
        """Process the dropped file and update the UI."""
        file_path = event.mimeData().urls()[0].toLocalFile()
        if self._is_valid_image(file_path):
            self.fileDropped.emit(file_path)
            self.update_label(file_path)
            event.accept()
        else:
            event.ignore()
    
    def update_label(self, file_path: str):
        """Update the label text with the dropped file name."""
        file_name = os.path.basename(file_path)
        self.setText(f"File loaded: {file_name}")
    
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