import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logging import get_logger
from src.core.error_handler import format_error, ImageProcessingError

# Initialize logger
logger = get_logger(__name__)

def main():
    """Entry point for the LogoCraft application."""
    try:
        # Initialize GUI application
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()

        logger.info("Application started successfully.")
        sys.exit(app.exec())

    except ImageProcessingError as e:
        logger.error(f"Image processing error: {format_error(e)}")
    except Exception as e:
        logger.critical(f"Fatal error: {format_error(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()