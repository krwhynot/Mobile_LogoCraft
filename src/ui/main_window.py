"""
Main window implementation for the HungerRush Image Processing Application.
Integrates all UI components and manages the overall application flow.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from pathlib import Path
import os

from src.services.image_processing_service import ImageProcessingService
from src.utils.logging import get_logger
from src.models.base import BaseImageProcessor
from .components.drop_zone import ImageDropZone
from .components.format_selector import FormatSelector
from .components.progress_indicator import ProgressIndicator
from .theme.colors import HungerRushColors, ThemeStyles, ThemeMode

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window integrating all UI components with HungerRush styling."""
    
    # Default paths for input and output
    DEFAULT_INPUT_PATH = str(Path.home() / "Desktop" / "Logo.png")
    DEFAULT_OUTPUT_PATH = str(Path.home() / "Desktop" / "processed_images")
    
    # Window settings
    WINDOW_TITLE = "HungerRush Image Processor"
    WINDOW_GEOMETRY = (200, 200, 600, 800)
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """
        Initialize the main window with all components and theme support.
        
        Args:
            theme_mode: The theme mode (light/dark) to apply
        """
        super().__init__()
        self.theme_mode = theme_mode
        
        # Initialize services and state
        self.processor = ImageProcessingService()
        self.current_file = None
        
        # Set up window properties
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(*self.WINDOW_GEOMETRY)
        
        # Initialize UI
        self._setup_ui()
        self._apply_theme()
        
        # Set default paths
        self._update_input_path(self.DEFAULT_INPUT_PATH)
        
        # Create processing timer for progress updates
        self._processing_timer = QTimer(self)
        self._processing_timer.timeout.connect(self._update_processing_progress)
        self._current_progress = 0
    
    def _setup_ui(self):
        """Set up the main user interface layout and components."""
        # Create main layout and central widget
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(int(ThemeStyles.SPACING['lg'].replace('px', '')))
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Initialize components
        self._setup_drop_zone()
        self._setup_input_section()
        self._setup_output_section()
        self._setup_format_selector()
        self._setup_process_button()
        self._setup_progress_indicator()
        
        # Set central widget
        self.setCentralWidget(self.central_widget)
    
    def _setup_drop_zone(self):
        """Initialize and configure the drop zone component."""
        self.drop_zone = ImageDropZone(self.theme_mode)
        self.drop_zone.fileDropped.connect(self._handle_file_drop)
        self.main_layout.addWidget(self.drop_zone)
    
    def _setup_input_section(self):
        """Set up the input file section."""
        section = self._create_section("Input Image")
        layout = QHBoxLayout()
        
        # Create and configure input file entry
        self.input_file_entry = QLineEdit()
        self.input_file_entry.setPlaceholderText("Select input image file...")
        self.input_file_entry.setReadOnly(True)
        
        # Create and configure browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_input_file)
        
        # Add widgets to layout
        layout.addWidget(self.input_file_entry)
        layout.addWidget(browse_button)
        
        # Add layout to section
        section.layout().addLayout(layout)
        self.main_layout.addWidget(section)
    
    def _setup_output_section(self):
        """Set up the output directory section."""
        section = self._create_section("Output Directory")
        layout = QHBoxLayout()
        
        # Create and configure output directory entry
        self.output_dir_entry = QLineEdit()
        self.output_dir_entry.setPlaceholderText("Select output directory...")
        self.output_dir_entry.setReadOnly(True)
        self.output_dir_entry.setText(self.DEFAULT_OUTPUT_PATH)
        
        # Create and configure browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_output_directory)
        
        # Add widgets to layout
        layout.addWidget(self.output_dir_entry)
        layout.addWidget(browse_button)
        
        # Add layout to section
        section.layout().addLayout(layout)
        self.main_layout.addWidget(section)
    
    def _setup_format_selector(self):
        """Set up the format selection section."""
        self.format_selector = FormatSelector(self.theme_mode)
        self.main_layout.addWidget(self.format_selector)
    
    def _setup_process_button(self):
        """Set up the process button."""
        self.process_button = QPushButton("Process Images")
        self.process_button.clicked.connect(self._process_images)
        self.process_button.setFixedWidth(200)  # Set a fixed width for better appearance
        self.main_layout.addWidget(self.process_button, alignment=Qt.AlignCenter)
    
    def _setup_progress_indicator(self):
        """Set up the progress indicator."""
        self.progress_indicator = ProgressIndicator(self.theme_mode)
        self.main_layout.addWidget(self.progress_indicator)
    
    def _create_section(self, title: str) -> QFrame:
        """
        Create a styled section frame with title.
        
        Args:
            title: The section title
            
        Returns:
            QFrame: The created section frame
        """
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(int(ThemeStyles.SPACING['md'].replace('px', '')))
        section.setLayout(layout)
        return section
    
    def _apply_theme(self):
        """Apply the HungerRush theme to the main window."""
        colors = HungerRushColors.LIGHT if self.theme_mode == ThemeMode.LIGHT else HungerRushColors.DARK
        
        # Main window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['bg_color']};
            }}
            
            QFrame {{
                background-color: {colors['section_bg']};
                border: 1px solid {colors['border_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['md']};
                padding: {ThemeStyles.SPACING['md']};
            }}
            
            QLineEdit {{
                background-color: {colors['input_bg']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
                padding: {ThemeStyles.STYLES['input']['padding']};
                min-height: {ThemeStyles.STYLES['input']['min_height']};
            }}
            
            QPushButton {{
                background-color: {colors['button_color']};
                color: white;
                border: none;
                border-radius: {ThemeStyles.BORDER_RADIUS['sm']};
                padding: {ThemeStyles.STYLES['button']['padding']};
                min-height: {ThemeStyles.STYLES['button']['min_height']};
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
        Handle dropped file and update UI.
        
        Args:
            file_path: Path to the dropped file
        """
        self._update_input_path(file_path)
    
    def _browse_input_file(self):
        """Handle input file browsing."""
        file_filter = f"Images ({' '.join(f'*{ext}' for ext in BaseImageProcessor.ALLOWED_FORMATS)})"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input Image", "", file_filter
        )
        if file_path:
            self._update_input_path(file_path)
    
    def _browse_output_directory(self):
        """Handle output directory selection."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if dir_path:
            self.output_dir_entry.setText(dir_path)
    
    def _update_input_path(self, file_path: str):
        """
        Update input path and related UI elements.
        
        Args:
            file_path: Path to the input file
        """
        self.input_file_entry.setText(file_path)
        self.drop_zone.update_label(file_path)
    
    def _start_processing_progress(self):
        """Start the progress update timer for processing feedback."""
        self._current_progress = 0
        self._processing_timer.start(100)  # Update every 100ms
        self.process_button.setEnabled(False)
    
    def _stop_processing_progress(self):
        """Stop the progress update timer and reset UI state."""
        self._processing_timer.stop()
        self._current_progress = 100
        self.progress_indicator.update_progress(100)
        self.process_button.setEnabled(True)
    
    def _update_processing_progress(self):
        """Update the progress bar during processing."""
        if self._current_progress < 90:  # Reserve last 10% for final processing
            self._current_progress += 2
            self.progress_indicator.update_progress(
                self._current_progress,
                "Processing images..."
            )
    
    def _process_images(self):
        """Process images with selected formats and provide user feedback."""
        try:
            # Input validation
            if not self._validate_inputs():
                return
            
            # Get processing parameters
            input_path = Path(self.input_file_entry.text())
            output_dir = Path(self.output_dir_entry.text())
            selected_formats = self.format_selector.get_selected()
            
            # Log processing start
            logger.info(f"Starting image processing:")
            logger.info(f"Input file: {input_path}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Selected formats: {selected_formats}")
            
            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Start progress updates
            self._start_processing_progress()
            self.progress_indicator.show_status("Preparing to process images...", "info")
            
            # Process images
            results = self.processor.process_batch(
                input_path, output_dir, selected_formats
            )
            
            # Stop progress updates
            self._stop_processing_progress()
            
            # Handle results
            self._handle_processing_results(results)
            
        except Exception as e:
            # Log and display error
            error_msg = f"Processing error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.progress_indicator.show_status(error_msg, "error")
            self._stop_processing_progress()
    
    def _validate_inputs(self) -> bool:
        """
        Validate all inputs before processing.
        
        Returns:
            bool: True if all inputs are valid, False otherwise
        """
        # Check input file
        if not self.input_file_entry.text():
            self.progress_indicator.show_status(
                "No input file selected!", "error"
            )
            return False
            
        input_path = Path(self.input_file_entry.text())
        if not input_path.exists():
            self.progress_indicator.show_status(
                "Input file does not exist!", "error"
            )
            return False
            
        # Check file extension
        if input_path.suffix.lower() not in BaseImageProcessor.ALLOWED_FORMATS:
            self.progress_indicator.show_status(
                f"Invalid file format! Allowed formats: {', '.join(BaseImageProcessor.ALLOWED_FORMATS)}",
                "error"
            )
            return False
        
        # Check output directory
        if not self.output_dir_entry.text():
            self.progress_indicator.show_status(
                "No output directory selected!", "error"
            )
            return False
        
        # Check format selection
        selected_formats = self.format_selector.get_selected()
        if not selected_formats:
            self.progress_indicator.show_status(
                "No formats selected!", "error"
            )
            return False
        
        return True
    
    def _handle_processing_results(self, results: list):
        """
        Handle the results of image processing and update UI accordingly.
        
        Args:
            results: List of processing results with status information
        """
        # Check for failed operations
        failed = [r["format"] for r in results if r["status"] == "failed"]
        
        if failed:
            # Some formats failed
            error_msg = f"Failed to process formats: {', '.join(failed)}"
            self.progress_indicator.show_status(error_msg, "error")
            logger.error(error_msg)
        else:
            # All formats succeeded
            success_msg = (
                f"Successfully processed {len(results)} formats!\n"
                f"Output saved to: {self.output_dir_entry.text()}"
            )
            self.progress_indicator.show_status(success_msg, "success")
            logger.info(success_msg)
    
    def closeEvent(self, event):
        """Handle application closure."""
        # Stop any ongoing processing
        if self._processing_timer.isActive():
            self._processing_timer.stop()
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())