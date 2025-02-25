"""
Main window implementation for the HungerRush Image Processing Application.
Integrates all UI components and manages the overall application flow.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QFileDialog, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QThread
from pathlib import Path

from src.services.image_processing_service import ImageProcessingService
from src.utils.logging import get_logger
from src.models.base import BaseImageProcessor
from src.ui.components.drop_zone import ImageDropZone
from src.ui.components.format_selector import FormatSelector
from src.ui.components.progress_indicator import ProgressIndicator
from src.ui.theme.colors import HungerRushColors, ThemeStyles, ThemeMode
from src.ui.components.file_section import FileSectionWidget
from src.ui.components.background_removal_option import BackgroundRemovalOption
from src.ui.components.message_dialogs import show_error, show_info, show_warning, show_confirmation
from src.ui.components.image_preview import ImagePreview
from src.utils.worker import ImageProcessingWorker

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window integrating all UI components with HungerRush styling."""

    # Default paths for input and output
    DEFAULT_OUTPUT_PATH = str(Path.home() / "Desktop" / "processed_images")

    # Window settings - using the specified initial size
    WINDOW_TITLE = "Mobile LogoCraft"
    WINDOW_WIDTH = 445
    WINDOW_HEIGHT = 820

    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """
        Initialize the main window with all components and theme support.

        Args:
            theme_mode: The theme mode (light/dark) to apply.
        """
        super().__init__()
        self.theme_mode = theme_mode

        # Initialize services and state
        self.processor = ImageProcessingService()
        self.current_file = None
        self.thread = None
        self.worker = None

        # Set up window properties
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)  # Initial size
        self.setMinimumSize(400, 600)  # Set minimum size for usability

        # Initialize UI
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        """Set up the main user interface layout and components."""
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Set up drop zone
        self._setup_drop_zone()
        
        # Set up image preview
        self.image_preview = ImagePreview(self.theme_mode)
        # Set size policy to make the image preview adjust with window size
        self.image_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_preview.setMinimumHeight(250)  # Minimum height for usability
        # Connect file drop signal from image preview
        self.image_preview.fileDropped.connect(self._handle_file_drop)
        self.main_layout.addWidget(self.image_preview, 1)  # Give stretch factor of 1

        # Set up file section
        self.file_section = FileSectionWidget(
            default_output_path=self.DEFAULT_OUTPUT_PATH,
            browse_input_callback=self._browse_input_file,
            browse_output_callback=self._browse_output_directory
        )
        self.main_layout.addWidget(self.file_section, 0)  # No stretch
        
        # Add background removal option
        self.bg_removal_option = BackgroundRemovalOption(self.theme_mode)
        # Updated fixed height to match component's new height
        self.bg_removal_option.setFixedHeight(110)
        # Add some extra space before the background removal option 
        self.main_layout.addSpacing(5)
        self.main_layout.addWidget(self.bg_removal_option, 0)  # No stretch
        # Add some extra space after the background removal option
        self.main_layout.addSpacing(5)

        self._setup_format_selector()
        self._setup_process_button()
        self._setup_progress_indicator()

        self.setCentralWidget(self.central_widget)

    def _setup_drop_zone(self):
        """Initialize and configure the drop zone component."""
        self.drop_zone = ImageDropZone(self.theme_mode)
        self.drop_zone.setFixedHeight(40)
        self.drop_zone.fileDropped.connect(self._handle_file_drop)
        self.main_layout.addWidget(self.drop_zone, 0)  # No stretch

    def _setup_format_selector(self):
        """Set up the format selection section."""
        self.format_selector = FormatSelector(self.theme_mode)
        # Allow format selector to adapt to available height
        self.format_selector.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.format_selector.setMinimumHeight(140)
        self.main_layout.addWidget(self.format_selector, 0)  # No stretch

    def _setup_process_button(self):
        """Set up the process button and cancel button."""
        # Create both buttons
        self.process_button = QPushButton("Process Images")
        self.process_button.clicked.connect(self._process_images)
        self.process_button.setFixedWidth(160)
        self.process_button.setFixedHeight(32)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._cancel_processing)
        self.cancel_button.setFixedWidth(160)
        self.cancel_button.setFixedHeight(32)
        self.cancel_button.hide()  # Initially hidden
        
        # Create a layout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.process_button, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)
        
        self.main_layout.addLayout(buttons_layout)

    def _setup_progress_indicator(self):
        """Set up the progress indicator."""
        self.progress_indicator = ProgressIndicator(self.theme_mode)
        self.progress_indicator.setFixedHeight(40)  # Increased height for better visibility
        self.progress_indicator.hide()  # Hide the progress indicator at startup
        self.main_layout.addWidget(self.progress_indicator, 0)  # No stretch

    def _apply_theme(self):
        """Apply the HungerRush theme to the main window."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['bg_color']};
            }}
            QLineEdit {{
                background-color: {colors['input_bg']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
                padding: 3px 5px;
                min-height: 22px;
                max-height: 22px;
            }}
            QPushButton {{
                background-color: {colors['button_color']};
                color: white;
                border: none;
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
                padding: 3px 8px;
                min-height: 22px;
                max-height: 22px;
            }}
            QPushButton:hover {{
                background-color: {HungerRushColors.SECONDARY_AQUA};
            }}
            QPushButton:pressed {{
                background-color: {HungerRushColors.PRIMARY_NAVY};
            }}
        """)

    def _handle_file_drop(self, file_path: str):
        """
        Handle a dropped file and update UI elements.

        Args:
            file_path: Path to the dropped file.
        """
        # Normalize path to use backslashes for display consistency
        normalized_path = str(Path(file_path)).replace("/", "\\")
        self._update_input_path(normalized_path)
        self.file_section.update_input_file(normalized_path)
        
        # Update the image preview
        self.image_preview.update_preview(file_path)

    def _browse_input_file(self):
        """Handle input file browsing."""
        file_filter = f"Images ({' '.join(f'*{ext}' for ext in BaseImageProcessor.ALLOWED_FORMATS)})"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input Image", str(Path.home() / "Desktop"), file_filter
        )
        if file_path:
            # Normalize path to use backslashes for display consistency
            normalized_path = str(Path(file_path)).replace("/", "\\")
            self._update_input_path(normalized_path)
            self.file_section.update_input_file(normalized_path)
            
            # Update the image preview
            self.image_preview.update_preview(file_path)

    def _browse_output_directory(self):
        """Handle output directory selection."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", str(Path.home() / "Desktop")
        )
        if dir_path:
            # Normalize path to use backslashes for display consistency
            normalized_path = str(Path(dir_path)).replace("/", "\\")
            self.file_section.output_dir_entry.setText(normalized_path)

    def _update_input_path(self, file_path: str):
        """
        Update the input path in both the file section and drop zone.

        Args:
            file_path: Path to the input file.
        """
        self.file_section.input_file_entry.setText(file_path)
        self.drop_zone.update_label(file_path)
        
        # Store the current file path
        self.current_file = file_path

    def _start_processing_progress(self):
        """Prepare the UI for image processing."""
        self.progress_indicator.reset()
        self.progress_indicator.show()  # Show the progress indicator when processing starts
        self.progress_indicator.show_status("Preparing...", "info")
        self.process_button.hide()
        self.cancel_button.show()

    def _stop_processing_progress(self):
        """Restore UI state after processing."""
        self.cancel_button.hide()
        self.process_button.show()
        # Don't hide the progress indicator immediately to allow the user to see the final status

    def _process_images(self):
        """Process images using the selected formats with a worker thread."""
        try:
            if not self._validate_inputs():
                return

            input_path = Path(self.file_section.input_file_entry.text())
            output_dir = Path(self.file_section.output_dir_entry.text())
            selected_formats = self.format_selector.get_selected()
            remove_background = self.bg_removal_option.is_background_removal_enabled()

            logger.info("Starting image processing:")
            logger.info(f"Input file: {input_path}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Selected formats: {selected_formats}")
            logger.info(f"Background removal: {remove_background}")

            # Prepare the UI
            self._start_processing_progress()
            
            # Create the processing thread
            self.thread = QThread()
            self.worker = ImageProcessingWorker(
                self.processor,
                input_path,
                output_dir,
                selected_formats,
                remove_background
            )
            
            # Move worker to thread
            self.worker.moveToThread(self.thread)
            
            # Connect signals and slots
            self.thread.started.connect(self.worker.process)
            self.worker.signals.finished.connect(self.thread.quit)
            self.worker.signals.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            # Connect progress signals
            self.worker.signals.progress.connect(self.progress_indicator.update_progress)
            self.worker.signals.status.connect(self.progress_indicator.show_status)
            self.worker.signals.error.connect(self._handle_processing_error)
            self.worker.signals.result.connect(self._handle_processing_results)
            
            # Connect cleanup
            self.thread.finished.connect(lambda: self._stop_processing_progress())
            
            # Start the thread
            self.thread.start()

        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.progress_indicator.show_status(error_msg, "error")
            self._stop_processing_progress()

    def _cancel_processing(self):
        """Cancel the current processing job."""
        if hasattr(self, 'worker') and hasattr(self, 'thread') and self.thread.isRunning():
            self.worker.cancel()
            self.progress_indicator.show_status("Cancelling...", "warning")

    def _handle_processing_error(self, error_message):
        """Handle errors from the worker thread."""
        logger.error(f"Processing error: {error_message}")
        self.progress_indicator.show_status(f"Error: {error_message}", "error")
        show_error(self, "Processing Error", error_message)

    def _validate_inputs(self):
        """
        Validate inputs before processing.

        Returns:
            True if all inputs are valid, False otherwise.
        """
        if not self.file_section.input_file_entry.text():
            self.progress_indicator.show()  # Show the progress indicator for error messages
            self.progress_indicator.show_status("No input file selected!", "error")
            show_error(self, "Input Error", "No input file selected!")
            return False

        input_path = Path(self.file_section.input_file_entry.text())
        if not input_path.exists():
            self.progress_indicator.show()  # Show the progress indicator for error messages
            self.progress_indicator.show_status("Input file does not exist!", "error")
            show_error(self, "File Error", "Input file does not exist!")
            return False

        if input_path.suffix.lower() not in BaseImageProcessor.ALLOWED_FORMATS:
            error_msg = f"Invalid file format! Allowed formats: {', '.join(BaseImageProcessor.ALLOWED_FORMATS)}"
            self.progress_indicator.show()  # Show the progress indicator for error messages
            self.progress_indicator.show_status(error_msg, "error")
            show_error(self, "Format Error", error_msg)
            return False

        if not self.file_section.output_dir_entry.text():
            self.progress_indicator.show()  # Show the progress indicator for error messages
            self.progress_indicator.show_status("No output directory selected!", "error")
            show_error(self, "Output Error", "No output directory selected!")
            return False

        if not self.format_selector.get_selected():
            self.progress_indicator.show()  # Show the progress indicator for error messages
            self.progress_indicator.show_status("No formats selected!", "error")
            show_error(self, "Selection Error", "No formats selected!")
            return False

        return True

    def _handle_processing_results(self, results: list):
        """
        Handle the results from image processing.

        Args:
            results: List of processing results.
        """
        failed = [r["format"] for r in results if r["status"] == "failed"]
        if failed:
            error_msg = f"Failed to process formats: {', '.join(failed)}"
            self.progress_indicator.show_status(error_msg, "error")
            show_error(self, "Processing Error", error_msg)
            logger.error(error_msg)
        else:
            success_msg = f"Successfully processed {len(results)} formats!"
            self.progress_indicator.show_status(success_msg, "success")
            show_info(self, "Success", success_msg)
            logger.info(success_msg)

    def closeEvent(self, event):
        """Handle application closure with confirmation if processing."""
        if hasattr(self, 'thread') and self.thread and self.thread.isRunning():
            # Processing is active, ask for confirmation
            if show_confirmation(self, "Confirm Exit", 
                               "Image processing is active. Are you sure you want to exit?"):
                # Cancel the worker and wait for the thread to finish
                if hasattr(self, 'worker') and self.worker:
                    self.worker.cancel()
                self.thread.quit()
                self.thread.wait(2000)  # Wait up to 2 seconds for clean shutdown
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
