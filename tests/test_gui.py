import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt  # ✅ Added missing import
from src.ui.main_window import MainWindow

@pytest.fixture(scope="module")
def app():
    """Creates a Qt application instance for GUI testing."""
    return QApplication.instance() or QApplication([])

@pytest.fixture
def main_window(qtbot):
    """Provides an instance of MainWindow for testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window

def test_main_window_loads(main_window):
    """Tests if the MainWindow loads correctly."""
    assert main_window.isVisible(), "Main window should be visible"

def test_main_window_has_widgets(main_window):
    """Tests if essential widgets exist in the GUI."""
    assert hasattr(main_window, "input_file_entry"), "Input file entry is missing"
    assert hasattr(main_window, "output_dir_entry"), "Output directory entry is missing"
    assert hasattr(main_window, "process_btn"), "Process Button is missing"
    assert hasattr(main_window, "status_label"), "Status label is missing"

def test_process_button_click(qtbot, main_window):
    """Simulates a click on the Process Button."""
    # Set required fields to avoid validation errors
    main_window.input_file_entry.setText("test.png")
    main_window.output_dir_entry.setText("output")

    # Click process button
    qtbot.mouseClick(main_window.process_btn, Qt.LeftButton)

    # Verify error message since file doesn't exist
    assert main_window.status_label.text() == "Processing error: No such file or directory", "Should show error for missing file"

def test_gui_close(qtbot, main_window):
    """Ensures the GUI closes properly without errors."""
    qtbot.wait(200)
    main_window.close()
    assert not main_window.isVisible(), "Main window should close successfully"
