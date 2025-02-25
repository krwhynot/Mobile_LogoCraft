"""
Centralized color and theme definitions for the HungerRush Image Processing Application.
This module provides a consistent color palette and theme settings across the application.
"""
from enum import Enum

class ThemeMode(Enum):
    """Theme mode enumeration for light and dark themes."""
    LIGHT = "light"
    DARK = "dark"

class HungerRushColors:
    """Centralized color definitions for the HungerRush theme system."""
    
    # Brand Colors - Primary Palette
    PRIMARY_TEAL = "#0E8476"  # Pantone 2244 C
    PRIMARY_NAVY = "#1A2639"  # Pantone 2766 C
    PRIMARY_GRAY = "#5F6369"  # Cool Gray 9 C
    
    # Brand Colors - Secondary Palette
    SECONDARY_BLUE = "#35508C"  # Pantone 2111 C
    SECONDARY_RED = "#FF585D"   # Pantone 178 C
    SECONDARY_AQUA = "#1D8296"  # Pantone 2223 C
    
    # UI State Colors
    SUCCESS = "#28A745"  # Success green
    ERROR = "#DC3545"    # Error red
    WARNING = "#ED9E24"  # Warning orange
    INFO = "#35508C"     # Info blue
    
    # Light Theme Color Scheme
    LIGHT = {
        "bg_color": "#FFFFFF",
        "section_bg": "#F5F7FA",
        "input_bg": "#FFFFFF",
        "button_color": PRIMARY_TEAL,
        "text_color": PRIMARY_NAVY,
        "text_secondary": PRIMARY_GRAY,
        "label_color": PRIMARY_NAVY,
        "checkbox_color": PRIMARY_NAVY,
        "border_color": "#E5E5E5",
        "hover_bg": "#E5F0EE"
    }
    
    # Dark Theme Color Scheme
    DARK = {
        "bg_color": "#1A2639",
        "section_bg": "#1E2B3E",
        "input_bg": "#FFFFFF",
        "button_color": "#23A47C",
        "text_color": "#23A47C",
        "text_secondary": "#A0A4B0",
        "label_color": "#23A47C",
        "checkbox_color": "#FFFFFF",
        "border_color": "#2A3A4F",
        "hover_bg": "#2C3D52"
    }

class ThemeStyles:
    """Common style definitions for consistent UI appearance."""
    
    # Spacing and Sizing
    SPACING = {
        "xs": "4px",
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "24px"
    }
    
    # Border Radii
    BORDER_RADIUS = {
        "sm": "4px",
        "md": "6px",
        "lg": "8px",
        "xl": "12px"
    }
    
    # Font Settings
    FONT = {
        "family": "Arial",
        "size": {
            "sm": "11px",
            "md": "13px",
            "lg": "15px",
            "xl": "18px"
        }
    }
    
    # Component-specific styles
    STYLES = {
        "button": {
            "min_height": "36px",
            "padding": f"{SPACING['sm']} {SPACING['md']}"
        },
        "input": {
            "min_height": "32px",
            "padding": SPACING['sm']
        },
        "checkbox": {
            "size": "16px",
            "padding": SPACING['sm']
        }
    }