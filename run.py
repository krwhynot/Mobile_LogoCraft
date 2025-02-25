"""
Launcher script for the Mobile LogoCraft application.
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Add project root to path for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import MainWindow
from src.ui.theme.colors import ThemeMode

def main():
    """Launch the Mobile LogoCraft application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Mobile LogoCraft")
    
    # Create and show the main window
    main_window = MainWindow(theme_mode=ThemeMode.DARK)
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
