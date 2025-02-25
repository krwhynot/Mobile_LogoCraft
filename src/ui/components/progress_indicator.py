"""
Enhanced progress indicator with animation and detailed status.
"""
from PySide6.QtWidgets import QWidget, QProgressBar, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from src.ui.theme.colors import HungerRushColors, ThemeMode
from src.utils.logging import get_logger

logger = get_logger(__name__)

class EnhancedProgressBar(QProgressBar):
    """Enhanced progress bar with smooth animations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)  # 300ms animation
        
    def setValue(self, value):
        """Animate the progress change."""
        if self.value() != value:
            self.animation.stop()
            self.animation.setStartValue(self.value())
            self.animation.setEndValue(value)
            self.animation.start()

class ProgressIndicator(QWidget):
    """Enhanced progress indicator with animation and detailed status."""
    
    def __init__(self, theme_mode=ThemeMode.DARK):
        super().__init__()
        self.theme_mode = theme_mode
        self.colors = HungerRushColors.LIGHT if theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        self._init_ui()
        self._apply_styles()
        
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Progress bar
        self.progress_bar = EnhancedProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("")  # Start with empty format to avoid "0% 0"
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
    def _apply_styles(self):
        """Apply styles to the components."""
        primary_color = HungerRushColors.PRIMARY_TEAL
        text_color = self.colors.get('text_color', '#1A1346')
        bg_color = self.colors.get('bg_color', '#FFFFFF')
        
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #E8ECF0;
                text-align: center;
                color: {text_color};
                font-size: 11px;
            }}
            
            QProgressBar::chunk {{
                background-color: {primary_color};
                border-radius: 4px;
            }}
            
            QLabel {{
                color: {text_color};
                font-size: 10px;
                margin-top: 2px;
            }}
        """)
        
    def reset(self):
        """Reset the progress indicator."""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")  # Clear format when resetting
        self.status_label.setText("")
        self.status_label.setStyleSheet(f"color: {self.colors.get('text_color', '#1A1346')};")
        
    def update_progress(self, value, status_text="", detail=""):
        """
        Update the progress bar and status text.
        
        Args:
            value: Progress percentage (0-100)
            status_text: Main status text
            detail: Optional detail text
        """
        self.progress_bar.setValue(value)
        
        # Only show percentage if greater than 0
        if value <= 0:
            self.progress_bar.setFormat("")
        elif detail:
            self.progress_bar.setFormat(f"{value}% - {detail}")
        else:
            self.progress_bar.setFormat(f"{value}%")
            
        if status_text:
            self.status_label.setText(status_text)
            
    def show_status(self, message, status_type="normal"):
        """
        Show a status message with appropriate styling.
        
        Args:
            message: Status message text
            status_type: Type of status (normal, info, success, error, warning)
        """
        self.status_label.setText(message)
        
        # Apply appropriate styling based on status type
        if status_type == "normal":
            self.status_label.setStyleSheet(f"color: {self.colors.get('text_color', '#1A1346')};")
        elif status_type == "info":
            self.status_label.setStyleSheet(f"color: {HungerRushColors.SECONDARY_BLUE};")
        elif status_type == "success":
            self.status_label.setStyleSheet(f"color: {HungerRushColors.ACCENT_GREEN};")
        elif status_type == "error":
            self.status_label.setStyleSheet(f"color: {HungerRushColors.SECONDARY_RED};")
        elif status_type == "warning":
            self.status_label.setStyleSheet(f"color: {HungerRushColors.ACCENT_ORANGE};")
