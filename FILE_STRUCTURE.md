# Mobile LogoCraft - Application Architecture

This document provides a complete overview of the Mobile LogoCraft application's structure, explaining the purpose of each directory and file, and how they interact to create a seamless image processing solution.

## Directory Structure

```
Mobile_LogoCraft/
├── assets/                    # Static assets (icons, images)
├── backup/                    # Backup files
├── deployment/                # Deployment configurations
├── docs/                      # Documentation
├── logs/                      # Application logs
├── resources/                 # Resource files
├── src/                       # Source code
│   ├── config/                # Configuration settings
│   │   ├── formats.py         # Image format definitions
│   │   └── __init__.py
│   ├── core/                  # Core functionality
│   │   ├── error_handler.py   # Error handling utilities
│   │   └── __init__.py
│   ├── models/                # Data models and processing logic
│   │   ├── background_remover.py  # Background removal functionality
│   │   ├── base.py            # Base image processor class
│   │   ├── image_processor.py # Image processing logic
│   │   ├── push_processor.py  # Push notification icon processor
│   │   └── __init__.py
│   ├── services/              # Business logic and services
│   │   ├── image_processing_service.py  # Image processing service
│   │   └── __init__.py
│   ├── ui/                    # User interface components
│   │   ├── components/        # Reusable UI components
│   │   │   ├── background_removal_option.py  # Background removal UI
│   │   │   ├── drop_zone.py   # Drag and drop zone
│   │   │   ├── file_section.py  # File input/output section
│   │   │   ├── format_selector.py  # Format selection UI
│   │   │   ├── message_dialogs.py  # Message dialog utilities
│   │   │   ├── progress_indicator.py  # Progress bar and status
│   │   │   └── __init__.py
│   │   ├── theme/             # Visual theming
│   │   │   ├── colors.py      # Color definitions and themes
│   │   │   ├── manager.py     # Theme management utilities
│   │   │   └── __init__.py
│   │   ├── main_window.py     # Main application window
│   │   └── __init__.py
│   ├── utils/                 # Utility functions
│   │   ├── file_utils.py      # File operation utilities
│   │   ├── image_utils.py     # Image manipulation utilities
│   │   ├── logging.py         # Logging configuration
│   │   └── __init__.py
│   ├── main.py                # Application entry point
│   └── __init__.py
├── tests/                     # Test cases
│   ├── assets/                # Test assets
│   ├── conftest.py            # PyTest configuration
│   ├── test_background_removal.py  # Background removal tests
│   ├── test_gui.py            # GUI tests
│   ├── test_image_processor.py  # Image processor tests
│   ├── test_integration.py    # Integration tests
│   ├── test_push_icon.py      # Push icon tests
│   ├── verify_output.py       # Output verification utilities
│   └── __init__.py
├── .gitignore                 # Git ignore file
├── requirements.txt           # Python dependencies
├── run.py                     # Application launcher script
└── run_app.ps1                # PowerShell launcher script
```

## Core Components

### Entry Points

The application has two primary entry points:

1. **run.py**: Primary entry point that sets up the application environment and launches the UI.
   ```python
   # Simplified example
   from src.ui.main_window import MainWindow
   
   def main():
       app = QApplication(sys.argv)
       main_window = MainWindow(theme_mode=ThemeMode.DARK)
       main_window.show()
       sys.exit(app.exec())
   ```

2. **src/main.py**: Core application logic that initializes the application, sets up error handling, and starts the UI.
   ```python
   # Simplified example
   def main():
       try:
           app = QApplication(sys.argv)
           window = MainWindow()
           window.show()
           sys.exit(app.exec())
       except Exception as e:
           logger.critical(f"Fatal error: {format_error(e)}")
   ```

### Configuration (src/config/)

The configuration module defines the supported image formats and processing settings:

- **formats.py**: Contains definitions for image formats, sizes, background colors, and quality settings.
  ```python
  FORMAT_CONFIGS = {
      "APPICON": {
          "size": (1024, 1024),
          "bg_color": (0, 0, 0, 0),  # Transparent
          "quality": 95,
          "description": "Application icon with optional transparency"
      },
      # Additional formats defined here
  }
  ```

### Models (src/models/)

The models directory contains classes for image processing:

- **base.py**: Base class with shared functionality for image processors.
  ```python
  class BaseImageProcessor:
      FORMAT_CONFIGS = FORMAT_CONFIGS
      ALLOWED_FORMATS = ALLOWED_FORMATS
      
      @classmethod
      def validate_input(cls, input_path, output_path):
          # Validation logic
  ```

- **image_processor.py**: Primary image processor that handles resizing and format conversion.
  ```python
  class ImageProcessor(BaseImageProcessor):
      def process_image(self, input_path, output_path, width, height, bg_color):
          # Image processing logic
          
      def process_format(self, input_path, output_path, format_name):
          # Format-specific processing
  ```

- **push_processor.py**: Specialized processor for creating push notification icons.
  ```python
  class PushProcessor:
      def create_push_notification(self, input_path, output_path, remove_background):
          # Push notification icon creation logic
  ```

- **background_remover.py**: Handles background removal with multiple methods.
  ```python
  class BackgroundRemover:
      def remove_background(self, image):
          # Background removal implementation
          
      def _remove_with_contour_detection(self, image):
          # Contour-based removal method
  ```

### Services (src/services/)

The services layer coordinates between UI and models:

- **image_processing_service.py**: Orchestrates the image processing workflow.
  ```python
  class ImageProcessingService:
      def process_batch(self, input_path, output_dir, selected_formats, remove_background):
          # Batch processing logic
          
      def process_single_format(self, input_path, output_dir, format_name, remove_background):
          # Single format processing
  ```

### User Interface (src/ui/)

The UI module contains all user interface components:

- **main_window.py**: Main application window that integrates all UI components.
  ```python
  class MainWindow(QMainWindow):
      def __init__(self, theme_mode):
          # Initialize UI components
          
      def _process_images(self):
          # Image processing workflow
  ```

- **components/**: Reusable UI components:
  - **drop_zone.py**: Drag-and-drop area for image input.
  - **format_selector.py**: UI for selecting output formats.
  - **progress_indicator.py**: Progress bar and status display.
  - **file_section.py**: File input/output management.
  - **background_removal_option.py**: Background removal toggle.
  - **message_dialogs.py**: Standardized message dialogs.

- **theme/**: Visual styling components:
  - **colors.py**: Color definitions and theme modes.
  - **manager.py**: Theme application utilities.

### Utilities (src/utils/)

Utility functions for common operations:

- **file_utils.py**: File operations like reading, writing, and validation.
- **image_utils.py**: Common image manipulation functions.
- **logging.py**: Logging configuration and utilities.

## Data Flow

The application follows this general flow:

1. **User Input**: User provides an input image via the drop zone or file browser.
2. **Format Selection**: User selects desired output formats via checkboxes.
3. **Processing Options**: User can enable background removal if needed.
4. **Validation**: The application validates inputs before processing.
5. **Processing**: The service layer orchestrates the processing workflow:
   - The `ImageProcessingService` coordinates the process.
   - For each format, it delegates to the appropriate processor:
     - Standard formats use `ImageProcessor`.
     - Push notification icons use `PushProcessor`.
   - Background removal is handled by `BackgroundRemover` when enabled.
6. **Output**: Processed images are saved to the specified directory.
7. **Feedback**: Progress and results are displayed to the user.

## Component Interactions

### UI to Service Layer

The main window connects to the service layer as follows:

```python
# In main_window.py
self.processor = ImageProcessingService()

def _process_images(self):
    # Get inputs from UI
    input_path = Path(self.file_section.input_file_entry.text())
    output_dir = Path(self.file_section.output_dir_entry.text())
    selected_formats = self.format_selector.get_selected()
    remove_background = self.bg_removal_option.is_background_removal_enabled()
    
    # Process images using the service
    result = self.processor.process_single_format(
        input_path, output_dir, format_name, remove_background
    )
```

### Service to Model Layer

The service layer delegates to appropriate models:

```python
# In image_processing_service.py
self.image_processor = ImageProcessor()
self.push_processor = PushProcessor()
self.background_remover = BackgroundRemover()

def _process_single_format(self, input_path, output_dir, format_name, remove_background):
    # For PUSH format, use specialized processor
    if format_name == "PUSH":
        self.push_processor.create_push_notification(input_path, output_path, remove_background)
    
    # For other formats with background removal
    if remove_background and supports_transparency:
        img = self.background_remover.remove_background(img)
    
    # Process using the standard processor
    self.image_processor.process_format(input_path, output_path, format_name)
```

### Model Interactions

Models interact with each other for specialized processing:

```python
# In push_processor.py
self.background_remover = BackgroundRemover()

def create_push_notification(self, input_path, output_path, remove_background):
    # Delegate background detection/removal to BackgroundRemover
    if remove_background:
        has_white_bg = self.background_remover.detect_white_background(cv2_img[:, :, :3])
        if has_white_bg:
            removed_bg = self.background_remover.remove_background(cv2_img[:, :, :3])
    
    # Apply specialized push icon processing
    processed = self.create_coloring_book_effect(img)
```

## Test Structure

The application includes comprehensive tests:

- **test_background_removal.py**: Tests for background removal functionality.
- **test_gui.py**: Tests for the graphical user interface components.
- **test_image_processor.py**: Tests for the core image processing functionality.
- **test_integration.py**: End-to-end tests of the entire application.
- **test_push_icon.py**: Tests for push notification icon creation.

## Deployment

The application can be deployed using:

- **run_app.ps1**: PowerShell script for launching on Windows.
- **deployment/**: Contains deployment configurations and scripts.

## Best Practices

The application follows several key architectural principles:

1. **Separation of Concerns**:
   - UI components are separate from business logic.
   - Processing logic is separated from service orchestration.

2. **Single Responsibility Principle**:
   - Each component has a clear, focused purpose.
   - UI components handle only UI concerns, models handle only processing, etc.

3. **Error Handling**:
   - Comprehensive error handling at all levels.
   - Clear error messages for users.

4. **Configurability**:
   - Formats and settings are centralized in the config module.
   - Easy to add or modify supported formats.

5. **Testability**:
   - Components are designed for easy testing.
   - Clear separation of concerns facilitates unit testing.

## Common Tasks

### Adding a New Format

To add a new format:

1. Add the format definition to `src/config/formats.py`:
   ```python
   FORMAT_CONFIGS = {
       # Existing formats...
       "NEW_FORMAT": {
           "size": (width, height),
           "bg_color": (r, g, b, a),
           "quality": 95,
           "description": "Description of the new format"
       },
   }
   ```

2. Add the format to the UI in `src/ui/components/format_selector.py`:
   ```python
   self.format_checkboxes = {
       # Existing formats...
       "NEW_FORMAT": QCheckBox("NEW_FORMAT")
   }
   ```

### Implementing a New Background Removal Method

To add a new background removal method:

1. Add the method to the `RemovalMethod` enum in `src/models/background_remover.py`:
   ```python
   class RemovalMethod(Enum):
       # Existing methods...
       NEW_METHOD = "new_method"
   ```

2. Implement the removal method in the `BackgroundRemover` class:
   ```python
   def _remove_with_new_method(self, image):
       # New background removal implementation
       # ...
       return result
   ```

3. Update the `remove_background` method to use the new method:
   ```python
   def remove_background(self, image):
       # ...
       elif self.method == RemovalMethod.NEW_METHOD:
           return self._remove_with_new_method(image)
       # ...
   ```

### Adding a New UI Component

To add a new UI component:

1. Create a new component file in `src/ui/components/`:
   ```python
   from PySide6.QtWidgets import QWidget
   
   class NewComponent(QWidget):
       def __init__(self, theme_mode):
           super().__init__()
           self.theme_mode = theme_mode
           self._setup_ui()
           
       def _setup_ui(self):
           # UI setup logic
   ```

2. Integrate the component into the main window in `src/ui/main_window.py`:
   ```python
   from src.ui.components.new_component import NewComponent
   
   def _setup_ui(self):
       # ...
       self.new_component = NewComponent(self.theme_mode)
       self.main_layout.addWidget(self.new_component)
   ```

## Conclusion

The Mobile LogoCraft application follows a clean, modular architecture that separates concerns and makes it easy to maintain and extend. The clear separation between UI, services, and models allows for flexible development and testing, while the central configuration system makes it easy to add or modify supported formats.
