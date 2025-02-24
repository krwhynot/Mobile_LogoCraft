from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from src.ui.theme.colors import HungerRushColors, ThemeStyles, ThemeMode  

class FileSectionWidget(QFrame):
    def __init__(self, default_output_path: str, browse_input_callback, browse_output_callback, theme_mode=ThemeMode.DARK, parent=None):
        super().__init__(parent)
        self.default_output_path = default_output_path
        self.browse_input_callback = browse_input_callback
        self.browse_output_callback = browse_output_callback
        self.theme_mode = theme_mode  # Store the theme mode

        # Enable styled background
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Apply the updated stylesheet using the correct theme
        self._apply_theme()
        self._setup_ui()

    def _apply_theme(self):
        """Apply theme-based background styling."""
        colors = HungerRushColors.DARK if self.theme_mode == ThemeMode.DARK else HungerRushColors.LIGHT
        self.setStyleSheet(f"""
            FileSectionWidget {{
                background-color: {colors["section_bg"]};
                border: 1px solid {colors["border_color"]};
                border-radius: {ThemeStyles.BORDER_RADIUS["md"]};
            }}

            QLabel {{
                color: {colors["label_color"]};
                font-size: {ThemeStyles.FONT["size"]["sm"]};
                font-family: {ThemeStyles.FONT["family"]};
                font-weight: bold;
            }}

            QLineEdit {{
                background-color: {colors["input_bg"]};
                color: {colors["text_color"]};
                border: 1px solid {colors["border_color"]};
                border-radius: {ThemeStyles.BORDER_RADIUS["sm"]};
                padding: 4px;
            }}

            QPushButton {{
                background-color: {colors["button_color"]};
                color: white;
                border: none;
                border-radius: {ThemeStyles.BORDER_RADIUS["sm"]};
                padding: 5px 8px;
            }}

            QPushButton:hover {{
                background-color: {HungerRushColors.SECONDARY_AQUA};
            }}

            QPushButton:pressed {{
                background-color: {HungerRushColors.PRIMARY_NAVY};
            }}
        """)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(6, 6, 6, 6)

        # Input file layout
        input_layout = QHBoxLayout()
        input_label = QLabel("Input File:")
        input_label.setFixedWidth(65)
        self.input_file_entry = QLineEdit()
        self.input_file_entry.setPlaceholderText("Select input image file...")
        self.input_file_entry.setReadOnly(True)
        browse_input_button = QPushButton("Browse")
        browse_input_button.setFixedWidth(65)
        browse_input_button.clicked.connect(self.browse_input_callback)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_file_entry)
        input_layout.addWidget(browse_input_button)

        # Output directory layout
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Dir:")
        output_label.setFixedWidth(65)
        self.output_dir_entry = QLineEdit()
        self.output_dir_entry.setPlaceholderText("Select output directory...")
        self.output_dir_entry.setReadOnly(True)
        self.output_dir_entry.setText(self.default_output_path)
        browse_output_button = QPushButton("Browse")
        browse_output_button.setFixedWidth(65)
        browse_output_button.clicked.connect(self.browse_output_callback)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_dir_entry)
        output_layout.addWidget(browse_output_button)

        layout.addLayout(input_layout)
        layout.addLayout(output_layout)

    def update_input_file(self, file_path: str):
        """Update the input file entry with the given file path."""
        self.input_file_entry.setText(file_path)
