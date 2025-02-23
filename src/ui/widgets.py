"""Reusable widgets for LogoCraft."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QGroupBox, QScrollArea, QMessageBox
)
from PySide6.QtCore import Signal
from typing import Set

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
