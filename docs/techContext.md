## File: delete_temp_files.py

**File Summary:** This script deletes temporary files from the `tests/assets/output/` directory.

**Dependencies:**

*   `pathlib`: Used for file path manipulation.

## File: requirements.txt

**File Summary:** This file lists the Python packages required to run the project.

**Dependencies:**

*   `wheel`
*   `setuptools`
*   `numpy`
*   `PySide6`
*   `Pillow`
*   `pytest`

## File: config.json

**File Summary:** This file contains configuration settings for the application, including output formats, processing parameters, and validation rules.

**Configuration Structure:**

*   `output`:
    *   `formats`:
        *   `APPICON`: `size`, `bg_color`
        *   `DEFAULT`: `size`, `bg_color`
        *   `DEFAULT_LG`: `size`, `bg_color`
        *   `DEFAULT_XL`: `size`, `bg_color`
        *   `FEATURE_GRAPHIC`: `size`, `bg_color`
        *   `LOGO`: `size`, `bg_color`
        *   `PUSH`: `size`, `bg_color`
*   `processing`:
    *   `max_file_size`
        *   `quality`
        *   `optimize`
        *   `progressive_jpeg`
*   `validation`:
    *   `min_dimension`
        *   `max_dimension`
        *   `allowed_formats`

## File: src/main.py

**File Summary:** This is the main entry point for the LogoCraft application. It initializes the GUI and handles any exceptions.

**Dependencies:**

*   `sys`
*   `PySide6.QtWidgets.QApplication`
*   `src.gui.main_window.MainWindow`
*   `src.core.config.Config`
*   `src.utils.logging.get_logger`
*   `src.core.error_handler.format_error`
*   `src.core.error_handler.ImageProcessingError`

**Functions:**

*   `main()`: Initializes the application, loads the configuration, initializes the GUI, and handles exceptions.

## File: src/core/config.py

**File Summary:** This file defines the `Config` class, a singleton that manages the application's configuration settings, loading them from a JSON file or initializing default values.

**Dependencies:**

*   `json`
*   `pathlib.Path`
*   `typing.Dict`
*   `typing.Any`
*   `typing.Optional`
*   `src.core.error_handler.ConfigurationError`
*   `src.utils.logging.get_logger`

**Constants:**

*   `DEFAULT_CONFIG`: A dictionary containing the default configuration settings.
*   `CONFIG_FILE_PATH`: A `Path` object representing the path to the configuration file ("config.json").

**Classes:**

*   `Config`: A singleton class that manages the application's configuration settings.
    *   `_instance`: A class-level attribute that stores the singleton instance.
    *   `_config`: A dictionary that stores the configuration settings.
    *   `__new__(cls)`: Overrides the default `__new__` method to implement the singleton pattern.
    *   `_validate_config_file(self) -> bool`: Validates that the config file exists and contains valid JSON data.
    *   `_load_or_initialize(self)`: Loads configuration from file or initializes default settings.
    *   `save_to_file(self)`: Saves the current configuration to a JSON file.
    *   `_validate_config(self, config: Dict[str, Any])`: Validates the configuration structure and content.
    *   `get(self, key: str, default: Optional[Any] = None) -> Any`: Retrieves a configuration value.
    *   `set(self, key: str, value: Any)`: Updates a configuration value and saves changes.

## File: src/core/error_handler.py

**File Summary:** This file defines custom exception classes for handling errors during image processing, validation, configuration, and file processing. It also includes functions for formatting and logging errors.

**Dependencies:**

*   `logging`

**Classes:**

*   `ImageProcessingError(Exception)`: Base exception for image processing errors.
    *   `ValidationError(ImageProcessingError)`: Exception for image validation failures.
    *   `ConfigurationError(Exception)`: Exception for configuration issues.
    *   `FileProcessingError(Exception)`: Exception for file-related issues.

**Functions:**

*   `format_error(error: Exception) -> str`: Formats an error message for better debugging and logging.
*   `log_error(error: Exception) -> None`: Logs an error using the standard logging system.

## File: src/core/format.py

**File Summary:** This file defines constants, a `NamedTuple` for format configuration, and functions related to image formats and file handling.

**Dependencies:**

*   `typing.NamedTuple`
*   `typing.Dict`
*   `typing.Tuple`

**Constants:**

*   `APP_NAME`: The name of the application ("LogoCraft").
*   `MIN_IMAGE_DIMENSION`: The smallest allowed image size (90).
*   `MAX_IMAGE_DIMENSION`: The largest allowed image size (5000).
*   `MAX_FILE_SIZE`: The maximum allowed file size (50MB).
*   `DEFAULT_QUALITY`: The default image quality setting (95).
*   `ALLOWED_FORMATS`: A set of allowed image file extensions.
*   `CHUNK_SIZE`: The chunk size for efficient file handling (1MB).
*   `ERROR_MESSAGES`: A dictionary of error messages.

**Classes:**

*   `FormatConfig(NamedTuple)`: Defines an image format's size and background color.
    *   `size`: A tuple representing the width and height of the image.
    *   `bg_color`: A tuple representing the background color (RGBA).

**Variables:**

*   `OUTPUT_FORMATS`: A dictionary mapping format names to `FormatConfig` instances.

**Functions:**

*   `get_format(name: str) -> FormatConfig`: Retrieves the format configuration by name.

## File: src/gui/widgets.py

**File Summary:** This file defines reusable widgets for the LogoCraft application, including a `DropArea` for image drag-and-drop, a `PreviewArea` for displaying image previews, and a `FormatSelector` for selecting output formats. It also includes helper functions for displaying error and warning messages.

**Dependencies:**

*   `PySide6.QtWidgets.QWidget`
*   `PySide6.QtWidgets.QVBoxLayout`
*   `PySide6.QtWidgets.QCheckBox`
*   `PySide6.QtWidgets.QGroupBox`
*   `PySide6.QtWidgets.QScrollArea`
*   `PySide6.QtWidgets.QLabel`
*   `PySide6.QtWidgets.QMessageBox`
*   `PySide6.QtCore.Qt`
*   `PySide6.QtCore.Signal`
*   `PySide6.QtGui.QPixmap`
*   `PySide6.QtGui.QImage`
*   `PySide6.QtGui.QDragEnterEvent`
*   `PySide6.QtGui.QDropEvent`
*   `PIL.ImageQt.ImageQt`
*   `PIL.Image.Image`
*   `pathlib.Path`
*   `typing.Set`
*   `src.core.config.Config`

**Classes:**

*   `DropArea(QLabel)`: A customized QLabel that accepts drag and drop of images.
    *   `dropped`: A signal emitted when a file is dropped or selected.
    *   `__init__(self)`: Initializes the drop area.
    *   `dragEnterEvent(self, event: QDragEnterEvent) -> None`: Handles the drag enter event.
    *   `dropEvent(self, event: QDropEvent) -> None`: Handles the drop event.
*   `PreviewArea(QWidget)`: A widget that displays a preview of the selected image.
    *   `__init__(self)`: Initializes the preview area.
    *   `update_preview(self, image_path: Path) -> None`: Updates the preview with the selected image.
    *   `clear(self) -> None`: Clears the preview image.

**Functions:**

*   `show_error(parent: QWidget, title: str, message: str) -> None`: Displays an error message dialog.
*   `show_warning(parent: QWidget, title: str, message: str) -> None`: Displays a warning message dialog.

## File: src/gui/components/dialogs.py

**File Summary:** This module provides a set of standardized dialog boxes for user interaction, ensuring consistent appearance and behavior across the application. It includes dialogs for confirmations, processing progress, and file overwrite confirmations.

**Dependencies:**

*   `typing.List`
*   `PySide6.QtWidgets.QMessageBox`
*   `PySide6.QtWidgets.QDialog`
*   `PySide6.QtWidgets.QVBoxLayout`
*   `PySide6.QtWidgets.QLabel`
*   `PySide6.QtWidgets.QPushButton`
*   `PySide6.QtWidgets.QProgressBar`
*   `PySide6.QtWidgets.QWidget`
*   `PySide6.QtWidgets.QHBoxLayout`
*   `PySide6.QtCore.Qt`
*   `PySide6.QtCore.Signal`
*   `src.gui.theme.HungerRushTheme`
*   `src.gui.theme.ComponentSize`
*   `src.gui.theme.ThemeMode`
*   `src.utils.ui_utils.show_error`
*   `src.utils.ui_utils.show_warning`
*   `src.utils.logging.get_logger`

**Functions:**

*   `confirm_action(parent: QWidget, title: str, message: str) -> bool`: Displays a confirmation dialog and returns the user's choice.

**Classes:**

*   `ProcessingDialog(QDialog)`: Dialog showing processing progress with a progress bar and status message.
    *   `cancelled`: A signal emitted when the processing is cancelled.
    *   `__init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.LIGHT)`: Initializes the processing dialog with theme support.
    *   `_setup_ui(self)`: Initializes the dialog's user interface with progress bar and controls.
    *   `update_progress(self, value: int, message: str = None)`: Updates the progress bar and optionally the status message.
    *   `_handle_cancel(self)`: Handles cancel button click by emitting signal and closing dialog.
*   `OverwriteDialog(QDialog)`: Dialog for confirming file overwrite with details about existing files.
    *   `__init__(self, files: List[str], parent=None, theme_mode: ThemeMode = ThemeMode.LIGHT)`: Initializes the overwrite confirmation dialog.
    *   `_setup_ui(self)`: Initializes the dialog's user interface with file list and controls.
    *   `_create_message_section(self) -> QVBoxLayout`: Creates the message and file list section of the dialog.
    *   `_create_button_section(self) -> QHBoxLayout`: Creates the button section of the dialog.
    *   `_handle_overwrite(self)`: Handles overwrite button click.
    *   `_handle_cancel(self)`: Handles cancel button click.

## File: src/gui/components/drop_area.py

**File Summary:** This module defines the `DropArea` component, a customized QLabel that accepts drag and drop of image files. It provides visual feedback and emits signals when files are dropped or selected via a file dialog.

**Dependencies:**

*   `pathlib.Path`
*   `typing.Dict`
*   `typing.Any`
*   `PySide6.QtWidgets.QLabel`
*   `PySide6.QtWidgets.QFileDialog`
*   `PySide6.QtWidgets.QWidget`
*   `PySide6.QtCore.Qt`
*   `PySide6.QtCore.Signal`
*   `PySide6.QtCore.QMimeData`
*   `PySide6.QtGui.QDragEnterEvent`
*   `PySide6.QtGui.QDropEvent`
*   `PySide6.QtGui.QDragLeaveEvent`
*   `src.core.config.Config`
*   `src.gui.theme.HungerRushTheme`
*   `src.gui.theme.ThemeMode`
*   `src.gui.theme.ComponentSize`
*   `src.utils.logging.get_logger`

**Classes:**

*   `DropArea(QLabel)`: A customized QLabel that accepts drag and drop of images.
    *   `file_dropped`: A signal emitted when a file is dropped or selected.
    *   `__init__(self)`: Initializes the drop area.
    *   `dragEnterEvent(self, event: QDragEnterEvent) -> None`: Handles the drag enter event.
    *   `dropEvent(self, event: QDropEvent) -> None`: Handles the drop event.
*   `PreviewArea(QWidget)`: A widget that displays a preview of the selected image.
    *   `__init__(self)`: Initializes the preview area.
    *   `update_preview(self, image_path: Path) -> None`: Updates the preview with the selected image.
    *   `clear(self) -> None`: Clears the preview image.

**Functions:**

*   `show_error(parent: QWidget, title: str, message: str) -> None`: Displays an error message dialog.
*   `show_warning(parent: QWidget, title: str, message: str) -> None`: Displays a warning message dialog.

## File: src/gui/components/format_selector.py

**File Summary:** This module defines the `FormatSelector` component, a widget for selecting output image formats with theme support. It uses checkboxes to allow users to choose which formats to generate.

**Dependencies:**

*   `typing.Set`
*   `typing.Dict`
*   `PySide6.QtWidgets.QWidget`
*   `PySide6.QtWidgets.QVBoxLayout`
*   `PySide6.QtWidgets.QGroupBox`
*   `PySide6.QtWidgets.QScrollArea`
*   `PySide6.QtWidgets.QCheckBox`
*   `PySide6.QtWidgets.QLabel`
*   `PySide6.QtWidgets.QHBoxLayout`
*   `PySide6.QtCore.Signal`
*   `PySide6.QtCore.Qt`
*   `src.core.config.Config`
*   `src.gui.theme.HungerRushTheme`
*   `src.gui.theme.ThemeMode`
*   `src.gui.theme.ComponentSize`
*   `src.utils.logging.get_logger`

**Classes:**

*   `FormatSelector(QWidget)`: Widget for selecting output image formats with theme support.
    *   `selection_changed`: A signal emitted when the selection changes.
    *   `__init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.LIGHT)`: Initializes the format selector.
    *   `_setup_ui(self)`: Initializes the UI with themed components.
    *   `_apply_group_style(self)`: Applies theme styling to group box.
    *   `_create_format_checkboxes(self)`: Creates themed checkboxes for each format.
    *   `_create_format_container(self, name: str, settings: dict) -> QWidget`: Creates a container for format selection with proper theming.
    *   `_get_checkbox_style(self) -> str`: Gets themed style for checkboxes.
    *   `_get_container_style(self) -> str`: Gets themed style for format containers.
    *   `_get_format_tooltip(self, name: str, settings: dict) -> str`: Generates format tooltip with theme colors.
    *   `_handle_checkbox_change(self, format_name: str, checked: bool)`: Handles checkbox state changes.
    *   `get_selected_formats(self) -> Set[str]`: Gets currently selected formats.
    *   `select_all(self)`: Selects all formats.
    *   `deselect_all(self)`: Deselects all formats.
    *   `reset(self)`: Resets to default state.
    *   `update_theme(self, theme_mode: ThemeMode)`: Updates component theme.

## File: src/gui/components/preview_area.py

**File Summary:** This module defines the `PreviewArea` component, a widget that displays a preview of the selected image with proper scaling and aspect ratio preservation.

**Dependencies:**

*   `pathlib.Path`
*   `PySide6.QtWidgets.QWidget`
*   `PySide6.QtWidgets.QVBoxLayout`
*   `PySide6.QtWidgets.QLabel`
*   `PySide6.QtCore.Qt`
*   `PySide6.QtCore.QSize`
*   `PySide6.QtGui.QPixmap`
*   `PySide6.QtGui.QImage`
*   `PIL.Image.Image`
*   `PIL.ImageQt.ImageQt`
*   `src.gui.theme.HungerRushTheme`
*   `src.gui.theme.ThemeMode`
*   `src.gui.theme.ComponentSize`
*   `src.utils.logging.get_logger`

**Classes:**

*   `PreviewArea(QWidget)`: A widget that displays a preview of the selected image with proper scaling and aspect ratio preservation.
    *   `__init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.LIGHT)`: Initializes the preview area.
    *   `_setup_ui(self)`: Initializes the preview area's user interface.
    *   `_apply_default_style(self)`: Applies the default theme styling.
    *   `_apply_error_style(self)`: Applies styling for error state.
    *   `update_preview(self, image_path: Path) -> None`: Updates the preview with the selected image.
    *   `clear(self) -> None`: Clears the preview image and reset styling.
    *   `resizeEvent(self, event)`: Handles resize events to maintain proper preview scaling.
    *   `update_theme(self, theme_mode: ThemeMode)`: Updates the widget's theme mode.

## File: src/gui/controllers/__init__.py

**File Summary:** This file initializes the `src.gui.controllers` package, exporting the `ImageController` class.

**Dependencies:**

*   `src.gui.controllers.image_controller.ImageController`

**Variables:**

*   `__all__`: A list containing the names of the modules to export (`['ImageController']`).

## File: src/gui/layout/__init__.py

**File Summary:** This file initializes the `src.gui.layout` package, exporting the `MainLayout` class.

**Dependencies:**

*   `src.gui.layout.main_layout.MainLayout`

**Variables:**

*   `__all__`: A list containing the names of the modules to export (`['MainLayout']`).

## File: src/gui/theme/__init__.py

**File Summary:** This file initializes the `src.gui.theme` package, defining enums for theme mode and component size, classes for theme colors and metrics, and the core `HungerRushTheme` class for theme management.

**Dependencies:**

*   `enum.Enum`
*   `PySide6.QtWidgets.QWidget`

**Enums:**

*   `ThemeMode(Enum)`: Defines the theme mode (LIGHT or DARK).
*   `ComponentSize(Enum)`: Defines component sizes (XS, SM, MD, LG, XL).

**Classes:**

*   `HungerRushColors`: Defines the color palette for the theme.
    *   `PRIMARY_TEAL`: Primary teal color.
    *   `PRIMARY_NAVY`: Primary navy color.
    *   `SECONDARY_BLUE`: Secondary blue color.
    *   `SECONDARY_RED`: Secondary red color.
    *   `SECONDARY_AQUA`: Secondary aqua color.
    *   `ACCENT_GREEN`: Accent green color.
    *   `ACCENT_ORANGE`: Accent orange color.
    *   `ACCENT_GOLD`: Accent gold color.
    *   `LIGHT_THEME`: Dictionary defining the light theme color palette.
    *   `DARK_THEME`: Dictionary defining the dark theme color palette.
*   `ThemeMetrics`: Defines spacing and border radius metrics for the theme.
*   `HungerRushTheme`: Core theme management for the application.
    *   `__init__(self, mode: ThemeMode = ThemeMode.LIGHT)`: Initializes the theme.
    *   `_get_color_palette(self, mode: ThemeMode)`: Returns the color palette based on the theme mode.
    *   `_get_metrics(self)`: Returns the theme metrics.
    *   `set_theme_mode(self, mode: ThemeMode)`: Updates the theme mode and recalculates colors.
    *   `apply_theme(self, widget)`: Applies the theme to a widget (placeholder).
    *   `get_button_style(self, button_type='primary', size=ComponentSize.MD)`: Generates button stylesheet based on type and size.

## File: src/gui/theme/theme_management.py

**File Summary:** This module defines the `ThemeManagementMixin` class, which provides consistent theme management capabilities for GUI components.

**Dependencies:**

*   `typing.Optional`
*   `PySide6.QtWidgets.QWidget`
*   `src.gui.theme.ThemeMode`
*   `src.gui.theme.HungerRushTheme`
*   `src.utils.logging.get_logger`

**Classes:**

*   `ThemeManagementMixin`: A mixin class to provide consistent theme management capabilities for GUI components.
    *   `__init__(self, parent: Optional[QWidget] = None, theme_mode: ThemeMode = ThemeMode.LIGHT)`: Initializes the theme management for the component.
    *   `update_theme(self, theme_mode: ThemeMode)`: Updates the theme for the current component and its children.
    *   `_apply_theme_style(self)`: Applies theme-specific styling to the component.
    *   `_update_child_themes(self, theme_mode: ThemeMode)`: Recursively update themes for child widgets.
    *   `set_theme_mode(self, theme_mode: ThemeMode)`: Convenience method to update theme mode.

## File: src/gui/theme/theme_manager.py

**File Summary:** This module defines the `ThemeManager` class, a centralized theme management utility that provides consistent theme application across the application.

**Dependencies:**

*   `PySide6.QtWidgets.QWidget`
*   `src.gui.theme.ThemeMode`
*   `src.gui.theme.HungerRushTheme`
*   `src.utils.logging.get_logger`

**Classes:**

*   `ThemeManager`: Centralized theme management for the application.
    *   `update_theme(widget: QWidget, theme_mode: ThemeMode)`: Universal theme update method for widgets.

## File: src/models/image_processing.py

**File Summary:** This module defines the `ImageProcessor` class, which handles basic image processing operations such as validation, orientation correction, resizing, and adding a background.

**Dependencies:**

*   `PIL.Image`
*   `PIL.ExifTags`
*   `PIL.ImageFilter`
*   `pathlib.Path`
*   `typing.Tuple`
*   `typing.Union`
*   `typing.List`
*   `typing.Dict`
*   `typing.TypedDict`
*   `src.core.error_handler.ImageProcessingError`
*   `src.core.config.Config`
*   `src.utils.logging.get_logger`

**Constants:**

*   `RESAMPLING_METHOD`: The resampling method used for resizing images (Image.LANCZOS).

**Classes:**

*   `ProcessingResults(TypedDict)`: Defines the structure for image processing results.
    *   `success`: List of successfully processed files.
    *   `failed`: List of files that failed to process.
*   `ImageProcessor`: Handles basic image processing operations.
    *   `DEFAULT_QUALITY`: Default image quality setting (95).
    *   `MIN_DIMENSION`: Minimum image dimension (90).
    *   `__init__(self)`: Initializes the image processor.
    *   `validate_image(self, img: Image.Image) -> None`: Validates image dimensions and format.
    *   `fix_orientation(self, img: Image.Image) -> Image.Image`: Corrects image orientation based on EXIF data.
    *   `resize_image(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image`: Resizes image while preserving aspect ratio.
    *   `process_image(self, input_path: Union[str, Path], output_path: Union[str, Path], target_width: int, target_height: int, bg_color: Tuple[int, int, int, int] = (255, 255, 255, 0)) -> bool`: Processes an image with resizing and optional background.

## File: src/models/push_icon_processor.py

**File Summary:** This module defines the `PushIconProcessor` class, which processes images step-by-step to create Android push notification icons. It includes various image processing techniques such as validation, resizing, grayscale conversion, contrast analysis, edge detection, and transparency application.

**Dependencies:**

*   `pathlib.Path`
*   `cv2`
*   `numpy`
*   `PIL.Image`
*   `PIL.ExifTags`
*   `PIL.ImageFilter`
*   `typing.Tuple`
*   `typing.Union`
*   `typing.List`
*   `typing.Dict`
*   `typing.TypedDict`
*   `src.core.error_handler.ImageProcessingError`
*   `src.core.config.Config`
*   `src.utils.logging.get_logger`

**Constants:**

*   `RESAMPLING_METHOD`: The resampling method used for resizing images (Image.LANCZOS).

**Classes:**

*   `ProcessingResults(TypedDict)`: Defines the structure for image processing results.
    *   `success`: List of successfully processed files.
    *   `failed`: List of files that failed to process.
*   `PushIconProcessor`: Processes images step-by-step to create Android push notification icons.
    *   `FILE_VALIDATION`: Dictionary containing file validation settings.
    *   `DIMENSION_VALIDATION`: Dictionary containing dimension validation settings.
    *   `MODE_SETTINGS`: Dictionary containing image mode conversion settings.
    *   `INTERMEDIATE_RESIZE`: Dictionary containing intermediate resize settings.
    *   `CHANNEL_SETTINGS`: Dictionary containing channel separation settings.
    *   `GRAY_CONVERSION`: Dictionary containing grayscale conversion settings.
    *   `CONTRAST_SETTINGS`: Dictionary containing contrast analysis settings.
    *   `TEXT_SETTINGS`: Dictionary containing text analysis settings.
    *   `BLUR_SETTINGS`: Dictionary containing blur application settings.
    *   `EDGE_SETTINGS`: Dictionary containing edge detection settings.
    *   `DILATION_SETTINGS`: Dictionary containing edge dilation settings.
    *   `THRESHOLD_SETTINGS`: Dictionary containing adaptive thresholding settings.
    *   `COMBINE_SETTINGS`: Dictionary containing mask combination settings.
    *   `MASK_SETTINGS`: Dictionary containing transparency mask settings.
    *   `FINAL_RESIZE`: Dictionary containing final resize settings.
    *   `FORMAT_SETTINGS`: Dictionary containing output format settings.
    *   `SAVE_SETTINGS`: Dictionary containing file saving settings.
    *   `__init__(self)`: Initializes the PushIconProcessor.
    *   `create_push_icon(self, input_path: Path, output_path: Path) -> bool`: Processes an image step-by-step to create a push notification icon.
    *   `_validate_file(self, input_path: Path)`: Checks file format and size.
    *   `_convert_mode(self, img: Image.Image) -> Image.Image`: Converts image to the target mode.
    *   `_resize_intermediate(self, img: Image.Image)`: Resizes image to intermediate processing size.
    *   `_convert_to_grayscale(self, img: Image.Image) -> np.ndarray`: Converts image to grayscale using OpenCV.
    *   `_analyze_contrast(self, gray_img: np.ndarray) -> float`: Analyzes contrast using histogram.
    *   `_apply_blur(self, img: np.ndarray, contrast_level: float) -> np.ndarray`: Applies Gaussian blur based on contrast.
    *   `_analyze_text(self, gray_img: np.ndarray) -> dict`: Analyzes text presence and characteristics in the image.
    *   `_detect_edges(self, img: np.ndarray, contrast_level: float) -> np.ndarray`: Detects edges using Canny edge detection.
    *   `_dilate_edges(self, edges: np.ndarray, text_info: dict) -> np.ndarray`: Dilates edges to enhance visibility.
    *   `_apply_threshold(self, img: np.ndarray, contrast_level: float) -> np.ndarray`: Applies adaptive thresholding.
    *   `_apply_transparency(self, img: Image.Image, mask: np.ndarray) -> Image.Image`: Applies transparency mask to create final image.
    *   `process_image(self, input_path: Path, output_path: Path, width: int, height: int) -> bool`: Processes an image with standard resizing.

## File: src/utils/file_utils.py

**File Summary:** This module defines the `FileUtils` class, which provides utility functions for file handling, validation, and directory management.

**Dependencies:**

*   `os`
*   `pathlib.Path`
*   `typing.List`
*   `typing.Set`
*   `typing.Union`
*   `logging`

**Constants:**

*   `VALID_EXTENSIONS`: A set of valid image file extensions.

**Classes:**

*   `FileUtils`: Utility functions for file handling, validation, and directory management.
    *   `create_output_directory(path: Union[str, Path]) -> None`: Creates a directory if it doesn't exist.
    *   `validate_path(path: Union[str, Path], must_exist: bool = True) -> Path`: Validates file path existence and format.
    *   `ensure_unique_path(path: Union[str, Path], pattern: str = "{name}_{index}{ext}") -> Path`: Generates a unique file path by appending an index if needed.
    *   `list_image_files(directory: Union[str, Path]) -> List[Path]`: Lists all valid image files in a directory.

## File: src/utils/image_utils.py

**File Summary:** This module defines the `ImageUtils` class, which provides utility functions for image validation, resizing, and format handling.

**Dependencies:**

*   `PIL.Image`
*   `typing.Tuple`
*   `typing.Union`
*   `pathlib.Path`
*   `logging`

**Constants:**

*   `MIN_DIMENSION`: The smallest allowed image size (90).
*   `MAX_DIMENSION`: The largest allowed image size (5000).
*   `CHUNK_SIZE`: The chunk size for efficient memory handling (1MB).

**Classes:**

*   `ImageUtils`: Utility functions for image validation, resizing, and format handling.
    *   `validate_image(img: Union[Image.Image, Path, str]) -> Tuple[bool, str]`: Validates image dimensions, format, and corruption checks.
    *   `optimal_downscale(img: Image.Image, target_size: Tuple[int, int], resampling=Image.LANCZOS) -> Image.Image`: Downscales an image while maintaining aspect ratio.
    *   `create_white_transparent(img: Image.Image, threshold: int = 128) -> Image.Image`: Converts all non-transparent pixels to white while preserving transparency.
    *   `convert_image_mode(img: Image.Image, required_mode: str = "RGBA") -> Image.Image`: Converts an image to a required mode.

## File: src/utils/logging.py

**File Summary:** This module provides centralized logging configuration using a singleton pattern, ensuring consistent logging across the application with both file and console output.

**Dependencies:**

*   `logging`
*   `logging.handlers`
*   `sys`
*   `time`
*   `datetime`
*   `pathlib.Path`
*   `typing.Optional`
*   `functools.lru_cache`

**Classes:**

*   `LoggerSingleton`: Singleton class to manage logging configuration across the application.
    *   `_instance`: A class-level attribute that stores the singleton instance.
    *   `_initialized`: A class-level attribute that indicates whether the logging has

## File: src/services/image_processing_service.py

**File Summary:** This module defines the `ImageProcessingService` class, which provides centralized image processing functionality decoupled from UI logic.

**Dependencies:**

*   `pathlib.Path`
*   `logging`
*   `src.models.image_processor.ImageProcessor`
*   `src.core.config.Config`
*   `src.utils.logging.get_logger`

**Classes:**

*   `ImageProcessingService`: Centralized service for managing image processing operations.
    *   `SUPPORTED_FORMATS`: A dictionary of supported image formats and their dimensions.
    *   `__init__(self, config=None)`: Initializes the image processing service.
    *   `process_batch(self, input_path, output_dir, selected_formats)`: Processes a batch of images in selected formats.
    *   `_process_single_format(self, input_path, output_dir, format_name)`: Processes a single image format.

## File: src/ui/main_window.py

**File Summary:** This file defines the `MainWindow` class, which is the main application window for the LogoCraft application.

**Dependencies:**

*   `PySide6.QtWidgets`
*   `PySide6.QtCore`
*   `PySide6.QtGui`
*   `pathlib.Path`
*   `src.services.image_processing_service.ImageProcessingService`
*   `src.core.config.Config`
*   `src.utils.logging.get_logger`

**Classes:**

*   `MainWindow`: Main application window.
    *   `__init__(self)`: Initializes the main window.
    *   `initUI(self)`: Initializes the GUI layout and components.
    *
