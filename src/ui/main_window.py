"""
Main window implementation for the LogoCraft application.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QFrame, QCheckBox, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
import os
from pathlib import Path

from src.services.image_processing_service import ImageProcessingService
from src.utils.logging import get_logger
from src.models.base import BaseImageProcessor

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main window for the LogoCraft application."""
    
    # Default paths
    DEFAULT_INPUT_PATH = r"C:\Users\Revadmin\Desktop\Logo.png"
    DEFAULT_OUTPUT_PATH = r"C:\Users\Revadmin\Desktop\test_images"
    
    # UI Settings
    WINDOW_TITLE = "HungerRush Utility - Image Processor"
    WINDOW_GEOMETRY = (200, 200, 500, 700)
    
    # Theme colors
    COLORS = {
        "bg_color": "#1A2639",
        "section_bg": "#1E2B3E",
        "input_bg": "#FFFFFF",
        "button_color": "#23A47C",
        "text_color": "#23A47C",
        "label_color": "#23A47C",
        "checkbox_color": "#FFFFFF"
    }
    
    # Style settings
    STYLES = {
        "border_radius": "4px",
        "font_family": "Arial",
        "font_size": 11,
        "padding": "8px 12px"
    }

    def __init__(self):
        super().__init__()
        
        # Initialize services and UI state
        self.processor = ImageProcessingService()
        self.current_file = None
        self.checkboxes = {}
        
        # Create a drop label for handling drop messages
        self.drop_label = QLabel("Drop image here or click Browse")
        self.drop_label.setStyleSheet(
            f"color: {self.COLORS['label_color']}; "
            "border: 2px dashed #aaa; "
            "border-radius: 5px; "
            "padding: 10px; "
            "text-align: center;"
        )
        
        # Set up UI
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(*self.WINDOW_GEOMETRY)
        self.setAcceptDrops(True)
        
        self.initUI()
        self._apply_theme()
        
        # Update drop label with default file
        self._update_drop_label(self.DEFAULT_INPUT_PATH)

    def initUI(self):
        """Initialize the UI layout and components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add drop label to layout
        main_layout.addWidget(self.drop_label)

        # Create sections
        self._create_input_section(main_layout)
        self._create_output_section(main_layout)
        self._create_format_section(main_layout)
        self._create_process_button(main_layout)
        
        # Add stretch to push everything up
        main_layout.addStretch()

        # Status Label
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _create_section_frame(self, title: str) -> tuple:
        """Create a styled section frame with title."""
        section_frame = QFrame()
        section_frame.setStyleSheet(
            f"background-color: {self.COLORS['section_bg']}; "
            f"border-radius: {self.STYLES['border_radius']}; "
            f"padding: 15px;"
        )
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(10)
        
        section_label = QLabel(title)
        section_label.setFont(QFont(self.STYLES['font_family'], self.STYLES['font_size']))
        section_label.setStyleSheet(f"color: {self.COLORS['label_color']};")
        section_layout.addWidget(section_label)
        
        return section_frame, section_layout

    def _create_input_section(self, main_layout: QVBoxLayout):
        """Create the input section of the GUI."""
        image_section, image_layout = self._create_section_frame("Input Image")
        
        # Input file entry and browse button
        input_layout = QHBoxLayout()
        
        self.input_file_entry = QLineEdit()
        self.input_file_entry.setPlaceholderText("Select input image file...")
        self.input_file_entry.setReadOnly(True)
        self.input_file_entry.setText(self.DEFAULT_INPUT_PATH)
        self.input_file_entry.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.input_file_entry)

        browse_button = QPushButton("Browse")
        browse_button.setStyleSheet(self._get_button_style())
        browse_button.clicked.connect(self._browse_input_file)
        input_layout.addWidget(browse_button)
        
        image_layout.addLayout(input_layout)
        main_layout.addWidget(image_section)

    def _create_output_section(self, main_layout: QVBoxLayout):
        """Create the output directory section."""
        output_section, output_layout = self._create_section_frame("Output Directory")
        
        output_layout = QHBoxLayout()
        
        self.output_dir_entry = QLineEdit()
        self.output_dir_entry.setPlaceholderText("Select output directory...")
        self.output_dir_entry.setReadOnly(True)
        self.output_dir_entry.setText(self.DEFAULT_OUTPUT_PATH)
        self.output_dir_entry.setStyleSheet(self._get_input_style())
        output_layout.addWidget(self.output_dir_entry)

        browse_button = QPushButton("Browse")
        browse_button.setStyleSheet(self._get_button_style())
        browse_button.clicked.connect(self._select_output_directory)
        output_layout.addWidget(browse_button)

        output_section.layout().addLayout(output_layout)
        main_layout.addWidget(output_section)

    def _create_format_section(self, main_layout: QVBoxLayout):
        """Create the format selection section."""
        format_section, format_layout = self._create_section_frame("Select Output Formats")
        
        grid_widget = QWidget()
        format_grid = QGridLayout(grid_widget)
        format_grid.setSpacing(10)
        
        formats = BaseImageProcessor.FORMAT_CONFIGS
        for i, (name, config) in enumerate(formats.items()):
            size = config["size"]
            checkbox = QCheckBox(f"{name} ({size[0]} × {size[1]} px)")
            # Only check the PUSH checkbox by default
            checkbox.setChecked(name == "PUSH")
            checkbox.setStyleSheet(
                f"QCheckBox {{"
                f"    color: {self.COLORS['checkbox_color']};"
                f"    padding: 5px;"
                f"}}"
                f"QCheckBox::indicator {{"
                f"    width: 16px;"
                f"    height: 16px;"
                f"}}"
                f"QCheckBox::indicator:unchecked {{"
                f"    border: 2px solid {self.COLORS['label_color']};"
                f"    background: transparent;"
                f"}}"
                f"QCheckBox::indicator:checked {{"
                f"    border: 2px solid {self.COLORS['button_color']};"
                f"    background: {self.COLORS['button_color']};"
                f"}}"
            )
            row, col = divmod(i, 2)
            format_grid.addWidget(checkbox, row, col)
            self.checkboxes[name] = checkbox

        format_layout.addWidget(grid_widget)
        main_layout.addWidget(format_section)

    def _create_process_button(self, main_layout: QVBoxLayout):
        """Create the process button."""
        self.process_btn = QPushButton("Process Images")
        self.process_btn.setFont(QFont(self.STYLES['font_family'], 10))
        self.process_btn.setStyleSheet(self._get_button_style(large=True))
        self.process_btn.clicked.connect(self._process_images)
        main_layout.addWidget(self.process_btn, alignment=Qt.AlignCenter)

    def _get_button_style(self, large=False) -> str:
        """Get style for buttons."""
        padding = "10px 20px" if large else "8px 12px"
        return (
            f"QPushButton {{"
            f"    background-color: {self.COLORS['button_color']};"
            f"    color: white;"
            f"    border: none;"
            f"    border-radius: {self.STYLES['border_radius']};"
            f"    padding: {padding};"
            f"}}"
            f"QPushButton:hover {{"
            f"    background-color: {self.COLORS['button_color']};"
            f"    opacity: 0.9;"
            f"}}"
            f"QPushButton:pressed {{"
            f"    background-color: {self.COLORS['button_color']};"
            f"    opacity: 0.8;"
            f"}}"
        )

    def _get_input_style(self) -> str:
        """Get style for input fields."""
        return (
            f"QLineEdit {{"
            f"    background-color: {self.COLORS['input_bg']};"
            f"    color: black;"
            f"    border: none;"
            f"    border-radius: {self.STYLES['border_radius']};"
            f"    padding: {self.STYLES['padding']};"
            f"}}"
        )

    def _apply_theme(self):
        """Apply theme to main window."""
        self.setStyleSheet(
            f"QMainWindow {{"
            f"    background-color: {self.COLORS['bg_color']};"
            f"}}"
            f"QWidget {{"
            f"    color: {self.COLORS['text_color']};"
            f"}}"
        )

    def _browse_input_file(self):
        """Handle input file browsing."""
        file_filter = f"Images ({' '.join(f'*{ext}' for ext in BaseImageProcessor.ALLOWED_FORMATS)})"
        file_path = QFileDialog.getOpenFileName(self, "Select Input Image", "", file_filter)[0]
        if file_path:
            self.input_file_entry.setText(file_path)
            self._update_drop_label(file_path)

    def _select_output_directory(self):
        """Handle output directory selection."""
        dir_name = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_name:
            self.output_dir_entry.setText(dir_name)

    def _process_images(self):
        """Process images in selected formats."""
        try:
            # Input validation
            if not self.input_file_entry.text():
                self._show_status("No input file selected!", error=True)
                return

            if not self.output_dir_entry.text():
                self._show_status("No output directory selected!", error=True)
                return

            selected_formats = [name for name, checkbox in self.checkboxes.items() 
                              if checkbox.isChecked()]
            
            if not selected_formats:
                self._show_status("No formats selected!", error=True)
                return

            input_path = Path(self.input_file_entry.text())
            output_dir = Path(self.output_dir_entry.text())

            logger.info(f"Starting image processing:")
            logger.info(f"Input file: {input_path}")
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Selected formats: {selected_formats}")

            # Process images
            results = self.processor.process_batch(input_path, output_dir, selected_formats)

            # Handle results
            failed = [r["format"] for r in results if r["status"] == "failed"]
            if failed:
                self._show_status(f"Failed to process formats: {', '.join(failed)}", error=True)
            else:
                self._show_status("Processing completed successfully!", success=True)

        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._show_status(error_msg, error=True)

    def _show_status(self, message: str, error: bool = False, success: bool = False):
        """Update status label with message."""
        color = ("#DC3545" if error else
                "#28A745" if success else
                self.COLORS["text_color"])
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.status_label.setText(message)

    def _update_drop_label(self, file_path: str):
        """Update drop zone label with file name."""
        self.drop_label.setText(f"File loaded: {os.path.basename(file_path)}")
        self.drop_label.setStyleSheet(
            f"color: {self.COLORS['label_color']}; "
            "font-weight: bold; "
            "border: 2px dashed #aaa; "
            "border-radius: 5px; "
            "padding: 10px; "
            "text-align: center;"
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop event."""
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.input_file_entry.setText(file_path)
        self._update_drop_label(file_path)
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())