"""
Format selector component for the HungerRush Image Processing Application.
Provides a grid-based interface for selecting output image formats with detailed information.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QGroupBox, 
    QGridLayout, QLabel
)
from PySide6.QtCore import Signal, Qt
from typing import Set

from ..theme.colors import HungerRushColors, ThemeStyles, ThemeMode
from src.config.formats import FORMAT_CONFIGS

class FormatSelector(QWidget):
    """Enhanced format selector with grid layout and detailed format information."""
    
    # Signal emitted when format selection changes
    selectionChanged = Signal(set)
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """
        Initialize the format selector with theme support.
        
        Args:
            theme_mode: The theme mode (light/dark) to apply
        """
        super().__init__()
        self.theme_mode = theme_mode
        self.selected = set()
        self.checkboxes = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the format selector user interface with a compact grid layout."""
        # Create main layout with minimal margins and spacing
        layout = QVBoxLayout(self)
        layout.setSpacing(0)  # Minimal spacing
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        
        # Create title label instead of group box to save space
        title_label = QLabel("Select Output Formats")
        title_label.setStyleSheet(self._get_title_style())
        title_label.setContentsMargins(8, 0, 0, 0)
        
        # Create grid layout for format options with minimal spacing
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(2)  # Minimal spacing between checkboxes
        grid.setContentsMargins(8, 4, 8, 4)  # Very small margins
        
        # Add format checkboxes to grid
        for i, (format_name, config) in enumerate(FORMAT_CONFIGS.items()):
            # Create checkbox with integrated dimension info
            dimensions = config["size"]
            cb = QCheckBox(f"{format_name.replace('_', ' ')} ({dimensions[0]}×{dimensions[1]} px)")
            cb.setStyleSheet(self._get_checkbox_style())
            
            # Calculate grid position (2 columns)
            row, col = divmod(i, 2)
            grid.addWidget(cb, row, col)
            
            # Connect checkbox signal and store reference
            # Only check the PUSH checkbox by default
            cb.setChecked(format_name == "PUSH")
            cb.stateChanged.connect(
                lambda state, n=format_name: self._on_selection_changed(n, bool(state))
            )
            self.checkboxes[format_name] = cb
            if format_name == "PUSH":
                self.selected.add(format_name)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(grid_widget)
        
        # Add background styling to the entire widget
        self.setStyleSheet(self._get_background_style())
    
    def _get_title_style(self) -> str:
        """Get the style for the title label."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        return f"""
            color: {colors['label_color']};
            font-family: {ThemeStyles.FONT['family']};
            font-size: {ThemeStyles.FONT['size']['sm']};
            font-weight: bold;
            padding: 4px 0;
        """
    
    def _get_background_style(self) -> str:
        """Get the style for the widget background."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        return f"""
            background-color: {colors['section_bg']};
            border: 1px solid {colors['border_color']};
            border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
        """
    
    def _get_checkbox_style(self) -> str:
        """Get the style for checkboxes."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        return f"""
            QCheckBox {{
                color: {colors['checkbox_color']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['sm']};
                padding: 1px;
                margin: 0;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border-radius: 2px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 1px solid {colors['border_color']};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                border: 1px solid {colors['button_color']};
                background: {colors['button_color']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {colors['button_color']};
            }}
        """
    
    def _on_selection_changed(self, format_name: str, checked: bool) -> None:
        """
        Update selected formats when a checkbox is clicked.
        
        Args:
            format_name: Name of the format being toggled
            checked: New state of the checkbox
        """
        if checked:
            self.selected.add(format_name)
        else:
            self.selected.discard(format_name)
        self.selectionChanged.emit(self.selected)
    
    def get_selected(self) -> Set[str]:
        """
        Return the set of selected output formats.
        
        Returns:
            Set of format names that are currently selected
        """
        return self.selected