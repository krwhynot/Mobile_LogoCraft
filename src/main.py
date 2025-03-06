import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.core.error_handler import format_error, ImageProcessingError

def main():
    """Entry point for the LogoCraft application."""
    try:
        # Initialize GUI application
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()

        # Run the application
        sys.exit(app.exec())

    except ImageProcessingError as e:
        print(f"Image processing error: {format_error(e)}")
    except Exception as e:
        print(f"Fatal error: {format_error(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
