from enum import Enum
from PySide6.QtWidgets import QWidget
from src.utils.logging import get_logger

logger = get_logger(__name__)

class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"

class ComponentSize(Enum):
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"

class HungerRushColors:
    PRIMARY_TEAL = "#00A4BD"
    PRIMARY_NAVY = "#1B365D"
    SECONDARY_BLUE = "#0078D4"
    SECONDARY_RED = "#D83B01"
    SECONDARY_AQUA = "#69797E"
    ACCENT_GREEN = "#107C10"
    ACCENT_ORANGE = "#D83B01"
    ACCENT_GOLD = "#FFB900"

    LIGHT_THEME = {
        "background": "#FFFFFF",
        "text": "#000000",
        "border": "#E5E5E5",
        "accent": PRIMARY_TEAL
    }

    DARK_THEME = {
        "background": "#1F1F1F",
        "text": "#FFFFFF",
        "border": "#404040",
        "accent": PRIMARY_NAVY
    }

class ThemeManager:
    """Centralized theme management for the application."""

    @staticmethod
    def update_theme(widget: QWidget, theme_mode: ThemeMode) -> None:
        """Universal theme update method for widgets.

        Args:
            widget: The widget to update
            theme_mode: The theme mode to apply
        """
        logger.debug(f"Updating theme for {widget.__class__.__name__} to {theme_mode.value}")

        colors = HungerRushColors.LIGHT_THEME if theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK_THEME

        # Apply base theme
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}

            QPushButton {{
                background-color: {colors['accent']};
                color: {'#000000' if theme_mode == ThemeMode.LIGHT else '#FFFFFF'};
                border-radius: 4px;
                padding: 6px 12px;
            }}

            QPushButton:hover {{
                background-color: {HungerRushColors.SECONDARY_BLUE};
            }}

            QLineEdit {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 4px;
            }}
        """)

        # Recursively update child widgets
        for child in widget.findChildren(QWidget):
            ThemeManager.update_theme(child, theme_mode)
