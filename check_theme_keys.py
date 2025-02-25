"""
Script to check for references to theme color keys that may be missing from the color dictionaries.
This helps identify potential KeyError issues before they occur at runtime.
"""
import os
import re
from pathlib import Path

# Root directory of the project
project_root = Path(__file__).parent

# Path to the UI components directory
ui_components_path = project_root / 'src' / 'ui' / 'components'
ui_path = project_root / 'src' / 'ui'

# Import the colors module to get the actual keys
from src.ui.theme.colors import HungerRushColors

# Get the actual keys in the LIGHT and DARK dictionaries
light_keys = set(HungerRushColors.LIGHT.keys())
dark_keys = set(HungerRushColors.DARK.keys())

# Regular expression to find color dictionary references: self.colors['key'] or colors['key']
color_ref_pattern = re.compile(r"(?:self\.colors|colors)\['([^']+)'\]")

def check_component_file(file_path):
    """Check a component file for color key references that might be missing."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all color key references
    matches = color_ref_pattern.findall(content)
    referenced_keys = set(matches)
    
    # Check if any referenced keys are missing from either theme
    missing_in_light = referenced_keys - light_keys
    missing_in_dark = referenced_keys - dark_keys
    
    if missing_in_light or missing_in_dark:
        print(f"\nFile: {file_path.relative_to(project_root)}")
        
        if missing_in_light:
            print(f"  Keys missing from LIGHT theme: {', '.join(missing_in_light)}")
        
        if missing_in_dark:
            print(f"  Keys missing from DARK theme: {', '.join(missing_in_dark)}")
            
        return True
    
    return False

def scan_directory(directory_path):
    """Recursively scan a directory for Python files and check them."""
    issues_found = False
    
    for path in directory_path.glob('**/*.py'):
        if path.is_file():
            if check_component_file(path):
                issues_found = True
    
    return issues_found

if __name__ == "__main__":
    print("Scanning for missing theme color keys...")
    
    # Check UI components directory
    if scan