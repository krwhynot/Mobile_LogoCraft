"""
Progress indicator component for the HungerRush Image Processing Application.
Provides visual feedback on processing status with a progress bar and status messages.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt

from ..theme.colors import HungerRushColors, ThemeStyles, ThemeMode

class ProgressIndicator(QWidget):
    """A comprehensive progress indicator with status messaging and visual feedback."""
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """
        Initialize the progress indicator with theme support.
        
        Args:
            theme_mode: The theme mode (light/dark) to apply
        """
        super().__init__()
        self.theme_mode = theme_mode
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the progress indicator user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(int(ThemeStyles.SPACING['md'].replace('px', '')))
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and configure progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        
        # Create status label for messages
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply HungerRush theme styling to the progress indicator."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        
        # Style the progress bar
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {colors['section_bg']};
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
                height: 8px;
            }}
            
            QProgressBar::chunk {{
                background-color: {colors['button_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
            }}
        """)
        
        # Style the status label
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_color']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['md']};
                padding: {ThemeStyles.SPACING['sm']};
            }}
        """)
    
    def update_progress(self, value: int, message: str = None):
        """
        Update the progress bar value and optionally display a status message.
        
        Args:
            value: Progress percentage (0-100)
            message: Optional status message to display
        """
        self.progress_bar.setValue(value)
        if message:
            self.show_status(message)
    
    def show_status(self, message: str, status_type: str = "normal"):
        """
        Display a status message with appropriate styling based on the message type.
        
        Args:
            message: The status message to display
            status_type: Type of status message ("normal", "success", "error", "warning")
        """
        # Define status colors
        status_colors = {
            "normal": HungerRushColors.LIGHT["text_color"] 
                     if self.theme_mode == ThemeMode.LIGHT 
                     else HungerRushColors.DARK["text_color"],
            "success": HungerRushColors.SUCCESS,
            "error": HungerRushColors.ERROR,
            "warning": HungerRushColors.WARNING,
            "info": HungerRushColors.INFO
        }
        
        # Apply status-specific styling
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_colors.get(status_type, status_colors["normal"])};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['md']};
                font-weight: bold;
                padding: {ThemeStyles.SPACING['sm']};
            }}
        """)
        
        self.status_label.setText(message)
    
    def reset(self):
        """Reset the progress indicator to its initial state."""
        self.progress_bar.setValue(0)
        self.status_label.clear()
        self._apply_style()  # Reset to normal styling