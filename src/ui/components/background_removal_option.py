"""
Background removal option UI component for the Mobile LogoCraft application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QCursor

from src.ui.theme.colors import HungerRushColors, ThemeMode, ThemeStyles
from src.utils.logging import get_logger

logger = get_logger(__name__)


class BackgroundRemovalOption(QWidget):
    """UI component for enabling background removal during image processing."""

    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """Initialize the background removal option component.

        Args:
            theme_mode: The theme mode (light/dark) to apply.
        """
        super().__init__()
        self.theme_mode = theme_mode
        self.colors = HungerRushColors.LIGHT if theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        self._init_ui()
        self._apply_styles()

    def _init_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        # Give much more room with larger margins
        layout.setContentsMargins(10, 8, 10, 10)
        # Significantly increase spacing between elements
        layout.setSpacing(8)

        # Header section with title and info button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        # Title
        title = QLabel("Background Removal")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)

        # Info button
        info_button = QPushButton()
        info_button.setIcon(QIcon(":/icons/info.png"))  # Fallback icon handling
        info_button.setIconSize(QSize(16, 16))
        info_button.setFixedSize(QSize(16, 16))
        info_button.setObjectName("infoButton")
        info_button.setCursor(QCursor(Qt.PointingHandCursor))
        info_button.setToolTip(
            "Automatically removes white backgrounds using Contour Detection.\n"
            "Best for logos and icons with distinct edges.\n"
            "Enable this for formats that support transparency."
        )
        header_layout.addWidget(info_button)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Checkbox
        self.checkbox = QCheckBox("Remove white background")
        self.checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.checkbox)

        # Description - ensure it has plenty of height
        description = QLabel(
            "Automatically detects and removes white backgrounds to create transparent images."
        )
        description.setWordWrap(True)
        description.setObjectName("descriptionText")
        # Significantly increase minimum height to ensure text is not cut off
        description.setMinimumHeight(45)
        layout.addWidget(description)

        # Add extra empty space at the bottom with a spacer
        layout.addSpacing(5)

        # Make the widget tall enough to accommodate everything with extra space
        self.setFixedHeight(110)

    def _apply_styles(self):
        """Apply styling to components."""
        try:
            # Get text color with fallback
            text_color = self.colors.get('text_color', HungerRushColors.PRIMARY_NAVY)
            secondary_color = self.colors.get('text_secondary', text_color)
            border_color = self.colors.get('border_color', '#E5E5E5')
            input_bg = self.colors.get('input_bg', '#FFFFFF')
            hover_bg = self.colors.get('hover_bg', '#E5F0EE')

            self.setStyleSheet(f"""
                #sectionTitle {{
                    color: {text_color};
                    font-weight: bold;
                    font-size: 13px;
                }}

                #descriptionText {{
                    color: {secondary_color};
                    font-size: 11px;
                    padding-bottom: 10px; /* Substantial padding at the bottom */
                    margin-bottom: 5px;   /* Extra margin to prevent text clipping */
                    line-height: 1.4;      /* Increase line spacing */
                }}

                QCheckBox {{
                    color: {text_color};
                }}

                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {border_color};
                    border-radius: 3px;
                    background-color: {input_bg};
                }}

                QCheckBox::indicator:checked {{
                    background-color: {HungerRushColors.PRIMARY_TEAL};
                    border-color: {HungerRushColors.PRIMARY_TEAL};
                }}

                #infoButton {{
                    background-color: transparent;
                    border: none;
                }}

                #infoButton:hover {{
                    background-color: {hover_bg};
                    border-radius: 8px;
                }}
            """)
        except Exception as e:
            logger.error(f"Error applying styles in BackgroundRemovalOption: {e}")
            # Apply fallback styles if theme colors are missing
            self.setStyleSheet("""
                #sectionTitle {
                    color: #1A1346;
                    font-weight: bold;
                    font-size: 13px;
                }

                #descriptionText {
                    color: #5F6369;
                    font-size: 11px;
                    padding-bottom: 10px; /* Substantial padding at the bottom */
                    margin-bottom: 5px;   /* Extra margin to prevent text clipping */
                    line-height: 1.4;      /* Increase line spacing */
                }

                QCheckBox {
                    color: #1A1346;
                }

                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #E5E5E5;
                    border-radius: 3px;
                    background-color: #FFFFFF;
                }

                QCheckBox::indicator:checked {
                    background-color: #0E8476;
                    border-color: #0E8476;
                }

                #infoButton {
                    background-color: transparent;
                    border: none;
                }

                #infoButton:hover {
                    background-color: #E5F0EE;
                    border-radius: 8px;
                }
            """)

    def is_background_removal_enabled(self) -> bool:
        """Check if background removal is enabled.

        Returns:
            True if background removal is enabled, False otherwise.
        """
        return self.checkbox.isChecked()
