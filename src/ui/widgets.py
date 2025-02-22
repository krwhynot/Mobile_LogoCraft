"""Reusable widgets for LogoCraft."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QGroupBox, QScrollArea, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PIL.ImageQt import ImageQt
from PIL import Image
from pathlib import Path
from typing import Set

class DropArea(QLabel):
    """Widget that allows drag-and-drop of images."""
    dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drop image here\nor click to browse")
        self.setMinimumSize(250, 250)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background: #f5f5f5;
                padding: 20px;
            }
            QLabel:hover {
                background: #e5e5e5;
                border-color: #999;
            }
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            self.dropped.emit(url.toLocalFile())
            break

class PreviewArea(QWidget):
    """Widget for displaying an image preview."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(200, 200)
        layout.addWidget(self.preview)

    def update_preview(self, image_path: Path) -> None:
        """Update the preview with the selected image."""
        try:
            with Image.open(image_path) as img:
                img.thumbnail((200, 200))
                qimage = ImageQt(img)
                pixmap = QPixmap.fromImage(qimage)
                self.preview.setPixmap(pixmap)
        except Exception as e:
            self.preview.setText(f"Preview failed: {str(e)}")

    def clear(self) -> None:
        """Clear the preview image."""
        self.preview.clear()

class FormatSelector(QWidget):
    """Widget to allow users to select output formats."""
    selectionChanged = Signal(set)

    # Output format configurations
    OUTPUT_FORMATS = {
        "APPICON": (1024, 1024),
        "DEFAULT": (1242, 1902),
        "DEFAULT_LG": (1242, 2208),
        "DEFAULT_XL": (1242, 2688),
        "FEATURE_GRAPHIC": (1024, 500),
        "LOGO": (1024, 1024),
        "PUSH": (96, 96)
    }

    def __init__(self):
        super().__init__()
        self.selected = set()
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the format selection UI."""
        layout = QVBoxLayout(self)
        group_box = QGroupBox("Select Output Formats")
        group_layout = QVBoxLayout(group_box)

        scroll = QScrollArea()
        scroll.setWidget(group_box)
        scroll.setWidgetResizable(True)

        self.checkboxes = {}

        for name, dimensions in self.OUTPUT_FORMATS.items():
            cb = QCheckBox(f"{name} ({dimensions[0]}×{dimensions[1]})")
            cb.setToolTip(f"Output format: {name}")
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, n=name: self._on_selection_changed(n, bool(state)))
            self.checkboxes[name] = cb
            group_layout.addWidget(cb)
            self.selected.add(name)

        layout.addWidget(scroll)

    def _on_selection_changed(self, format_name: str, checked: bool) -> None:
        """Update selected formats when a checkbox is clicked."""
        if checked:
            self.selected.add(format_name)
        else:
            self.selected.discard(format_name)
        self.selectionChanged.emit(self.selected)

    def get_selected(self) -> Set[str]:
        """Return the set of selected output formats."""
        return self.selected

def show_error(parent: QWidget, title: str, message: str) -> None:
    """Display an error message dialog."""
    QMessageBox.critical(parent, title, message)

def show_warning(parent: QWidget, title: str, message: str) -> None:
    """Display a warning message dialog."""
    QMessageBox.warning(parent, title, message)