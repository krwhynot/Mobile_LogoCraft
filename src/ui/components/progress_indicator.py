"""
Progress indicator component for the HungerRush Image Processing Application.
Provides visual feedback on processing status with a progress bar and status messages.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

from ..theme.colors import HungerRushColors, ThemeStyles, ThemeMode

class ProgressIndicator(QWidget):
    """A compact progress indicator with status messaging and visual feedback."""
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """
        Initialize the progress indicator with theme support.
        
        Args:
            theme_mode: The theme mode (light/dark) to apply
        """
        super().__init__()
        self.theme_mode = theme_mode
        self._setup_ui()
        self._animation = None
    
    def _setup_ui(self):
        """Set up the progress indicator user interface with horizontal layout for compactness."""
        layout = QHBoxLayout(self)
        layout.setSpacing(6)  # Slightly increased spacing for better readability
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        
        # Create and configure progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)  # Slightly taller for better visibility
        
        # Create status label for messages
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_label.setFixedHeight(16)  # Fixed height for status label
        
        # Add widgets to layout
        layout.addWidget(self.progress_bar, 7)  # 70% of space
        layout.addWidget(self.status_label, 3)  # 30% of space
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply enhanced HungerRush theme styling to the progress indicator."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        primary_color = HungerRushColors.PRIMARY_TEAL
        
        # Enhanced progress bar styling with gradient and border effects
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {colors['section_bg']};
                border-radius: 3px;
                height: 6px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {primary_color}, 
                    stop:1 {HungerRushColors.SECONDARY_AQUA}
                );
                border-radius: 3px;
            }}
        """)
        
        # Style the status label
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_color']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['sm']};
                padding: 0;
            }}
        """)
    
    def update_progress(self, value: int, message: str = None, format_name: str = None):
        """
        Update the progress bar value with smooth animation and display status and format information.
        
        Args:
            value: Progress percentage (0-100)
            message: Optional status message to display
            format_name: The format currently being processed
        """
        # Cancel any existing animation
        if self._animation is not None:
            self._animation.stop()
        
        # Create smooth animation for progress update
        self._animation = QPropertyAnimation(self.progress_bar, b"value")
        self._animation.setDuration(300)  # 300ms animation
        self._animation.setStartValue(self.progress_bar.value())
        self._animation.setEndValue(value)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)  # Smooth curve
        self._animation.start()
        
        # Format the status message with current format information if available
        display_message = message
        if format_name:
            display_message = f"Processing {format_name}" + (f": {message}" if message else "")
            
        if display_message:
            # Keep message short for horizontal layout
            short_message = display_message[:25] + "..." if len(display_message) > 25 else display_message
            self.show_status(short_message)
    
    def show_status(self, message: str, status_type: str = "normal"):
        """
        Display a status message with appropriate styling based on the message type.
        
        Args:
            message: The status message to display
            status_type: Type of status message ("normal", "success", "error", "warning", "info")
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
                font-size: {ThemeStyles.FONT['size']['sm']};
                padding: 0;
            }}
        """)
        
        self.status_label.setText(message)
    
    def reset(self):
        """Reset the progress indicator to its initial state with animation."""
        self.update_progress(0)
        self.status_label.clear()
        self._apply_style()  # Reset to normal styling