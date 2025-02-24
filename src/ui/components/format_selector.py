"""
Format selector component for the HungerRush Image Processing Application.
Provides a grid-based interface for selecting output image formats with detailed information.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QGroupBox, 
    QGridLayout, QLabel
)
from PySide6.QtCore import Signal, Qt
from typing import Set, Dict, Tuple

from ..theme.colors import HungerRushColors, ThemeStyles, ThemeMode

class FormatSelector(QWidget):
    """Enhanced format selector with grid layout and detailed format information."""
    
    # Signal emitted when format selection changes
    selectionChanged = Signal(set)
    
    # Output format configurations with dimensions and descriptions
    OUTPUT_FORMATS: Dict[str, Tuple[Tuple[int, int], str]] = {
        "APPICON": (
            (1024, 1024),
            "Application icon with optional transparency"
        ),
        "DEFAULT": (
            (1242, 1902),
            "Standard splash screen with maintained aspect ratio"
        ),
        "DEFAULT_LG": (
            (1242, 2208),
            "Large splash screen for higher resolution devices"
        ),
        "DEFAULT_XL": (
            (1242, 2688),
            "Extra large splash screen for modern devices"
        ),
        "FEATURE_GRAPHIC": (
            (1024, 500),
            "Feature graphic banner for store listings"
        ),
        "LOGO": (
            (1024, 1024),
            "High-resolution square logo with transparency"
        ),
        "LOGO_WIDE": (
            (1024, 500),
            "High-resolution wide logo with transparency"
        ),
        "PUSH": (
            (96, 96),
            "Small notification icon (white with transparency)"
        )
    }
    
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
        """Set up the format selector user interface with a direct grid layout."""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(int(ThemeStyles.SPACING['md'].replace('px', '')))
        
        # Create group box for formats
        group_box = QGroupBox("Select Output Formats")
        group_box.setStyleSheet(self._get_group_box_style())
        
        # Create grid layout for format options
        grid = QGridLayout(group_box)
        grid.setSpacing(int(ThemeStyles.SPACING['lg'].replace('px', '')))
        
        # Add format checkboxes to grid
        for i, (format_name, (dimensions, description)) in enumerate(self.OUTPUT_FORMATS.items()):
            # Create format container
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setSpacing(int(ThemeStyles.SPACING['xs'].replace('px', '')))
            container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for tighter layout
            
            # Create and style checkbox
            cb = QCheckBox(format_name.replace('_', ' '))  # Add space between words for better readability
            cb.setStyleSheet(self._get_checkbox_style())
            
            # Create and style dimension label
            dim_label = QLabel(f"{dimensions[0]}×{dimensions[1]} px")
            dim_label.setStyleSheet(self._get_label_style())
            
            # Add tooltip with full description
            container.setToolTip(f"{description}\nDimensions: {dimensions[0]}×{dimensions[1]} px")
            
            # Add widgets to container
            container_layout.addWidget(cb)
            container_layout.addWidget(dim_label)
            
            # Calculate grid position (2 columns)
            row, col = divmod(i, 2)
            grid.addWidget(container, row, col)
            
            # Connect checkbox signal and store reference
            # Only check the PUSH checkbox by default
            cb.setChecked(format_name == "PUSH")
            cb.stateChanged.connect(
                lambda state, n=format_name: self._on_selection_changed(n, bool(state))
            )
            self.checkboxes[format_name] = cb
            if format_name == "PUSH":
                self.selected.add(format_name)
        
        # Add group box directly to layout without scroll area
        layout.addWidget(group_box)
    
    def _get_group_box_style(self) -> str:
        """Get the style for the group box."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        return f"""
            QGroupBox {{
                background-color: {colors['section_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['md']};
                margin-top: 1.5em;
                padding: {ThemeStyles.SPACING['lg']};
                font-family: {ThemeStyles.FONT['family']};
            }}
            QGroupBox::title {{
                color: {colors['label_color']};
                subcontrol-origin: margin;
                left: {ThemeStyles.SPACING['md']};
                padding: 0 {ThemeStyles.SPACING['sm']};
                font-weight: bold;
            }}
        """
    
    def _get_checkbox_style(self) -> str:
        """Get the style for checkboxes."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        return f"""
            QCheckBox {{
                color: {colors['checkbox_color']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['md']};
                padding: {ThemeStyles.SPACING['sm']};
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: {ThemeStyles.STYLES['checkbox']['size']};
                height: {ThemeStyles.STYLES['checkbox']['size']};
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {colors['border_color']};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {colors['button_color']};
                background: {colors['button_color']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {colors['button_color']};
            }}
        """
    
    def _get_label_style(self) -> str:
        """Get the style for dimension labels."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        return f"""
            QLabel {{
                color: {colors['text_color']};
                font-family: {ThemeStyles.FONT['family']};
                font-size: {ThemeStyles.FONT['size']['sm']};
                padding-left: {ThemeStyles.SPACING['lg']};
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