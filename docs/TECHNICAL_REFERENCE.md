# Mobile LogoCraft Technical Reference

This document provides a comprehensive technical reference of the Mobile LogoCraft application, detailing the exact order of operations, file dependencies, and function descriptions.

## Order of Operations

### 1. Application Initialization

1. **File: `src/main.py`**
   - **Function: `main()`**
     - Initializes the `QApplication` instance
     - Creates the `MainWindow` instance
     - Shows the window and starts the event loop
     - Wraps execution in try/except to handle any unhandled exceptions

### 2. User Interface Initialization

1. **File: `src/ui/main_window.py`**
   - **Function: `__init__()`**
     - Initializes the `ImageProcessingService` instance
     - Sets up window properties (title, size)
     - Calls `_setup_ui()` to create UI components
     - Calls `_apply_theme()` to apply HungerRush styling

   - **Function: `_setup_ui()`**
     - Creates the main layout container
     - Calls component setup methods in sequence:
       - `_setup_drop_zone()`
       - Creates `ImagePreview` instance
       - Creates `FileSectionWidget` instance
       - Creates `BackgroundRemovalOption` instance
       - `_setup_format_selector()`
       - `_setup_process_button()`
       - `_setup_progress_indicator()`

   - **Function: `_apply_theme()`**
     - Applies the HungerRush theme styling to all components

### 3. User Input Handling

1. **File: `src/ui/components/drop_zone.py`**
   - **Class: `ImageDropZone`**
     - Handles drag-and-drop events
     - Emits `fileDropped` signal when a file is dropped

2. **File: `src/ui/components/image_preview.py`**
   - **Class: `ImagePreview`**
     - Also handles drag-and-drop events
     - Displays a preview of the selected image
     - Emits `fileDropped` signal when a file is dropped

3. **File: `src/ui/main_window.py`**
   - **Function: `_handle_file_drop()`**
     - Processes dropped files
     - Updates UI components with file path
     - Updates image preview

   - **Function: `_browse_input_file()`**
     - Opens file dialog for image selection
     - Updates UI components with selected file path
     - Updates image preview

   - **Function: `_browse_output_directory()`**
     - Opens directory dialog for output location
     - Updates output directory entry field

4. **File: `src/ui/components/format_selector.py`**
   - **Class: `FormatSelector`**
     - Displays checkboxes for available output formats
     - Provides `get_selected()` method to retrieve selected formats

5. **File: `src/ui/components/background_removal_option.py`**
   - **Class: `BackgroundRemovalOption`**
     - Provides toggle for background removal
     - Offers tooltip explaining functionality

### 4. Image Processing Initiation

1. **File: `src/ui/main_window.py`**
   - **Function: `_process_images()`**
     - Called when Process button is clicked
     - Calls `_validate_inputs()` to check inputs
     - Collects selected formats and options
     - Creates worker thread for background processing
     - Sets up signal/slot connections
     - Calls `_start_processing_progress()` to update UI

   - **Function: `_validate_inputs()`**
     - Validates input file existence and format
     - Validates output directory
     - Checks that at least one format is selected
     - Shows error messages for invalid inputs

2. **File: `src/utils/worker.py`**
   - **Class: `ImageProcessingWorker`**
     - **Function: `process()`**
       - Executes processing in background thread
       - Emits progress and status signals
       - Emits final results signal

### 5. Image Processing Execution

1. **File: `src/services/image_processing_service.py`**
   - **Function: `process_batch()`**
     - Processes a batch of image formats
     - Creates output directory if it doesn't exist
     - Iterates through selected formats, calling `_process_single_format()`
     - Returns processing results

   - **Function: `_process_single_format()`**
     - Processes a single image format
     - Special handling for PUSH format using `PushProcessor`
     - Detects if background removal is needed based on format and user selection
     - Returns result dictionary with status and output path

2. **File: `src/models/push_processor.py`**
   - **Function: `create_push_notification()`**
     - Specialized processing for PUSH format
     - Creates white icon on transparent background
     - Uses `BackgroundRemover` for transparency handling

3. **File: `src/models/background_remover.py`**
   - **Function: `remove_background()`**
     - Main entry point for background removal
     - Calls `detect_white_background()` to check if removal is needed
     - Determines which removal method to use
     - Defaults to combined pipeline for best results

   - **Function: `_remove_with_combined_pipeline()`**
     - Implements the complete 7-step background removal pipeline:
       1. Calls `_contour_detection_method()`
       2. Calls `_threshold_method()`
       3. Calls `_combine_masks()`
       4. Calls `_apply_morphological_operations()`
       5. Calls `_refine_contours()`
       6. Calls `_final_cleanup()`
       7. Calls `_apply_transparency()`

4. **File: `src/models/image_processor.py`**
   - **Function: `process_format()`**
     - Processes an image for a specific predefined format
     - Gets format configuration from `BaseImageProcessor.FORMAT_CONFIGS`
     - Calls `process_image()` with format-specific parameters

   - **Function: `process_logo()`**
     - Special handling for LOGO formats (square and wide variants)
     - Applies custom processing for logos

   - **Function: `process_image()`**
     - Core image processing function
     - Handles image loading, resizing, and positioning
     - Preserves aspect ratio as needed
     - Applies background color if specified
     - Saves output image

### 6. Results Handling

1. **File: `src/utils/worker.py`**
   - **Class: `WorkerSignals`**
     - Provides signal definitions for worker communication
     - Emits progress, status, error, and result signals

2. **File: `src/ui/main_window.py`**
   - **Function: `_handle_processing_results()`**
     - Processes final results from worker thread
     - Shows success or error messages
     - Updates progress indicator with final status

   - **Function: `_handle_processing_error()`**
     - Handles errors from worker thread
     - Shows error dialog with details
     - Updates progress indicator with error status

   - **Function: `_stop_processing_progress()`**
     - Restores UI state after processing completes
     - Switches back to Process button from Cancel button

## Detailed File and Function Descriptions

### 1. Main Application (`src/main.py`)

- **Function: `main()`**
  - **Purpose:** Application entry point
  - **Dependencies:** MainWindow, QApplication
  - **Operation:** Initializes the application, handles top-level exceptions

### 2. Main Window (`src/ui/main_window.py`)

- **Class: `MainWindow`**
  - **Purpose:** Main application window and controller
  - **Dependencies:**
    - ImageProcessingService
    - ImageDropZone
    - ImagePreview
    - FileSectionWidget
    - BackgroundRemovalOption
    - FormatSelector
    - ProgressIndicator
    - ImageProcessingWorker

  - **Function: `__init__()`**
    - **Purpose:** Initialize window and services
    - **Operation:** Sets up window properties and initializes UI

  - **Function: `_setup_ui()`**
    - **Purpose:** Create and arrange UI components
    - **Operation:** Creates main layout and adds all UI components

  - **Function: `_handle_file_drop()`**
    - **Purpose:** Process dropped files
    - **Operation:** Updates UI with file path and preview

  - **Function: `_process_images()`**
    - **Purpose:** Start image processing
    - **Operation:** Validates inputs, creates worker thread, connects signals

  - **Function: `_validate_inputs()`**
    - **Purpose:** Check all inputs before processing
    - **Operation:** Validates file paths and selected formats

  - **Function: `_handle_processing_results()`**
    - **Purpose:** Process and display final results
    - **Operation:** Shows success or error messages

### 3. Image Processing Service (`src/services/image_processing_service.py`)

- **Class: `ImageProcessingService`**
  - **Purpose:** Coordinate image processing operations
  - **Dependencies:**
    - BackgroundRemover
    - ImageProcessor
    - PushProcessor

  - **Function: `process_batch()`**
    - **Purpose:** Process multiple formats for a single input
    - **Operation:** Iterates through selected formats, creating output files

  - **Function: `_process_single_format()`**
    - **Purpose:** Process a single image format
    - **Operation:** Handles format-specific processing logic

### 4. Background Remover (`src/models/background_remover.py`)

- **Class: `BackgroundRemover`**
  - **Purpose:** Handle background removal operations
  - **Dependencies:** OpenCV (cv2), NumPy

  - **Function: `remove_background()`**
    - **Purpose:** Remove background from image
    - **Operation:** Applies background removal pipeline

  - **Function: `_remove_with_combined_pipeline()`**
    - **Purpose:** Apply complete 7-step background removal
    - **Operation:** Implements sophisticated background removal

  - **Function: `detect_white_background()`**
    - **Purpose:** Determine if image has white background
    - **Operation:** Analyzes border pixels to detect background

  - **Function: `convert_to_white_icon()`**
    - **Purpose:** Convert image to white with transparency
    - **Operation:** Creates white icon for PUSH format

### 5. Image Processor (`src/models/image_processor.py`)

- **Class: `ImageProcessor`**
  - **Purpose:** Handle image resizing and format processing
  - **Dependencies:** PIL (Pillow), BaseImageProcessor

  - **Function: `process_image()`**
    - **Purpose:** Core image processing
    - **Operation:** Handles loading, resizing, positioning, and saving

  - **Function: `process_format()`**
    - **Purpose:** Process predefined formats
    - **Operation:** Uses format configurations to process images

  - **Function: `process_logo()`**
    - **Purpose:** Specialized logo processing
    - **Operation:** Handles specific requirements for logo formats

### 6. Push Processor (`src/models/push_processor.py`)

- **Class: `PushProcessor`**
  - **Purpose:** Create PUSH notification icons
  - **Dependencies:** BackgroundRemover, PIL (Pillow)

  - **Function: `create_push_notification()`**
    - **Purpose:** Generate PUSH format icon
    - **Operation:** Creates 96x96 white icon with transparency

### 7. Base Image Processor (`src/models/base.py`)

- **Class: `BaseImageProcessor`**
  - **Purpose:** Provide base functionality and constants
  - **Dependencies:** None

  - **Class Variables:**
    - `ALLOWED_FORMATS`: List of supported file extensions
    - `FORMAT_CONFIGS`: Dictionary of format specifications

### 8. Worker Thread Implementation (`src/utils/worker.py`)

- **Class: `ImageProcessingWorker`**
  - **Purpose:** Handle background processing
  - **Dependencies:** QThread, ImageProcessingService

  - **Function: `process()`**
    - **Purpose:** Execute processing in background
    - **Operation:** Runs image processing without blocking UI

  - **Function: `cancel()`**
    - **Purpose:** Cancel ongoing processing
    - **Operation:** Sets cancellation flag

## Component Dependencies

### Core Dependencies

- **MainWindow** depends on:
  - ImageProcessingService
  - UI components

- **ImageProcessingService** depends on:
  - BackgroundRemover
  - ImageProcessor
  - PushProcessor

- **ImageProcessor** depends on:
  - BaseImageProcessor

- **PushProcessor** depends on:
  - BackgroundRemover
  - BaseImageProcessor

### UI Component Dependencies

- **FormatSelector** depends on:
  - BaseImageProcessor (for format configs)

- **ImagePreview** depends on:
  - PIL (for image loading and preview)

- **ProgressIndicator** depends on:
  - ThemeColors (for styling)

## Execution Flow Diagram

```
main.py
  └── MainWindow.__init__()
      ├── ImageProcessingService.__init__()
      │   ├── BackgroundRemover.__init__()
      │   ├── ImageProcessor.__init__()
      │   └── PushProcessor.__init__()
      ├── MainWindow._setup_ui()
      └── MainWindow._apply_theme()
          
User interactions (file selection, format selection)
  └── MainWindow._process_images()
      ├── MainWindow._validate_inputs()
      ├── MainWindow._start_processing_progress()
      └── ImageProcessingWorker.process()
          └── ImageProcessingService.process_batch()
              └── For each format:
                  └── ImageProcessingService._process_single_format()
                      ├── If PUSH format:
                      │   └── PushProcessor.create_push_notification()
                      │       └── BackgroundRemover.remove_background()
                      │           └── BackgroundRemover._remove_with_combined_pipeline()
                      │               └── 7-step background removal process
                      └── If other format:
                          ├── Optional BackgroundRemover.remove_background()
                          └── ImageProcessor.process_format() or process_logo()
                              └── ImageProcessor.process_image()
                                  
Results handling
  └── MainWindow._handle_processing_results()
      └── MainWindow._stop_processing_progress()
```

## Format-Specific Processing Logic

### PUSH Format (96x96 px)

1. Uses `PushProcessor.create_push_notification()`
2. If background removal is enabled:
   - Applies `BackgroundRemover.remove_background()`
   - Sets all non-transparent pixels to white using `convert_to_white_icon()`
3. Resizes to 96x96 px
4. Saves as PNG with transparency

### LOGO Formats (1024x1024 and 1024x500 px)

1. Uses `ImageProcessor.process_logo()`
2. If background removal is enabled and white background is detected:
   - Applies `BackgroundRemover.remove_background()`
3. Resizes while preserving aspect ratio
4. Centers in output canvas
5. Saves as PNG with transparency

### APPICON Format (1024x1024 px)

1. Uses `ImageProcessor.process_format()`
2. If background removal is enabled and white background is detected:
   - Applies `BackgroundRemover.remove_background()`
3. Resizes to 1024x1024 px
4. Saves as PNG with optional transparency

### DEFAULT Formats (Splash Screens)

1. Uses `ImageProcessor.process_format()`
2. Resizes to target dimensions while preserving aspect ratio
3. Centers in output canvas
4. Applies solid background color
5. Saves as PNG

### FEATURE_GRAPHIC Format (1024x500 px)

1. Uses `ImageProcessor.process_format()`
2. Resizes to 1024x500 px while preserving aspect ratio
3. Centers in output canvas
4. Applies solid background color
5. Saves as PNG

## Background Removal Pipeline Details

### 1. Contour Detection (`_contour_detection_method()`)

- Convert to grayscale
- Apply Gaussian blur to reduce noise
- Use Canny edge detection
- Dilate edges to close gaps
- Find contours and fill them

### 2. Thresholding (`_threshold_method()`)

- Convert to grayscale
- Apply Gaussian blur
- Use Otsu's thresholding method

### 3. Mask Combination (`_combine_masks()`)

- Combine contour and threshold masks using bitwise OR

### 4. Morphological Operations (`_apply_morphological_operations()`)

- Apply morphological closing to fill small holes
- Use elliptical kernel for natural results

### 5. Contour Refinement (`_refine_contours()`)

- Find contours in combined mask
- Filter small contours (noise)
- Create clean mask with significant contours only

### 6. Final Cleanup (`_final_cleanup()`)

- Apply additional morphological closing
- Fill any remaining small holes

### 7. Transparency Application (`_apply_transparency()`)

- Convert BGR to BGRA
- Use refined mask as alpha channel
