# Mobile LogoCraft
Mobile LogoCraft is an application designed to automatically generate multiple-sized images from a single input, specifically tailored for application development and marketing materials.

## Features
- Generates multiple image sizes from a single input
- Supports common image formats (PNG, JPG, JPEG, GIF, BMP, TIFF, JIFIF)
- Maintains image quality using LANCZOS resampling
- Preserves aspect ratios
- Supports transparent backgrounds
- User-friendly GUI with drag-and-drop functionality
- Real-time progress tracking
- Comprehensive error handling
- Sophisticated background removal pipeline
- Format-specific processing optimizations

## Installation

### Method 1: Using pip (Recommended)
1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

2. Install Mobile LogoCraft:

```powershell
pip install mobile-logocraft
```

### Method 2: From source
1. Clone the repository:

```powershell
git clone https://github.com/hungerrush/mobile-logocraft.git
cd mobile-logocraft
```

2. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Install the package in development mode:

```powershell
pip install -e .
```

## Running the Application

### Method 1: Using the executable
1. Download the latest release from the releases page
2. Double-click `mobile-logocraft.exe` to run

### Method 2: Using Python
1. Activate your virtual environment if not already activated:

```powershell
.\venv\Scripts\Activate
```

2. Run the application:

```powershell
python -m mobile_logocraft
```

## Output Formats
The application generates the following image formats:

| Format | Dimensions | Description |
|--------|------------|-------------|
| APPICON | 1024×1024 px | Application icon with transparency |
| DEFAULT | 1242×1902 px | Standard splash screen |
| DEFAULT_LG | 1242×2208 px | Large splash screen |
| DEFAULT_XL | 1242×2688 px | Extra large splash screen |
| FEATURE_GRAPHIC | 1024×500 px | Feature graphic for store listings |
| LOGO | 1024×1024 px | High-resolution square logo |
| LOGO_WIDE | 1024×500 px | High-resolution wide logo |
| PUSH | 96×96 px | Small notification icon (white with transparency) |

## Basic Usage
1. Launch the application
2. Drag and drop your image or click "Browse" to select it
3. Choose which output formats you want to generate
4. Select your output directory
5. Click "Process Image"
6. Wait for the processing to complete
7. Check your output directory for the generated images

## Codebase Structure
```
src/
├── config/                            # Configuration files
│   └── formats.py                     # Image format configurations
├── controllers/                       # Controller classes
├── core/                             # Core functionality
│   └── error_handler.py              # Error handling utilities
├── models/                           # Business logic models
│   ├── background_remover.py         # Background removal functionality
│   ├── base.py                       # Base image processor class
│   ├── image_processor.py            # Main image processing logic
│   └── push_processor.py             # Push notification icon processor
├── services/
│   └── image_processing_service.py   # Service for coordinating image processing
├── ui/                               # User interface components
│   ├── components/                   # Reusable UI components
│   │   ├── background_removal_option.py # Background removal toggle
│   │   ├── drop_zone.py             # Drag and drop zone
│   │   ├── file_section.py          # File input/output section
│   │   ├── format_selector.py       # Format selection grid
│   │   ├── image_preview.py         # Image preview component
│   │   ├── message_dialogs.py       # Message dialog utilities
│   │   └── progress_indicator.py    # Progress bar and status
│   ├── main_window.py               # Main application window
│   └── theme/                       # Theming and styling
│       └── colors.py                # Color definitions and theme utilities
└── utils/                           # Utility functions
    ├── logging.py                   # Logging configuration
    └── worker.py                    # Background worker thread implementation
```

## Technical Details

### Background Removal Pipeline
The application implements a sophisticated background removal process:

1. **Contour Detection**: Identifies the boundaries of distinct objects
2. **Thresholding**: Separates foreground from background based on pixel intensity
3. **Mask Combination**: Merges results from multiple methods
4. **Morphological Operations**: Cleans up the mask by filling small holes
5. **Contour Refinement**: Further refines by focusing on significant contours
6. **Final Cleanup**: Final polish of the mask
7. **Transparency Application**: Creates a transparent PNG with background removed

### Key Components
- **MainWindow**: Main application window with all UI components and event handling
- **ImageProcessingService**: Coordinates image processing operations
- **BackgroundRemover**: Implements background removal pipeline
- **ImageProcessor**: Handles image resizing and format-specific processing
- **ImageProcessingWorker**: Handles background processing to keep UI responsive


## Order of Operations

### 1. Application Entry Point (`src/main.py`)
The application starts in `main.py`, which serves as the entry point:

- **main()**: Initializes the QApplication and MainWindow, then runs the application event loop
- Handles top-level exceptions with proper error formatting

### 2. Main Window Setup (`src/ui/main_window.py`)
The MainWindow class initializes the UI and sets up event handlers:

- **__init__()**: Initializes the main window and services
- **_setup_ui()**: Creates the main layout and adds all UI components
- **_setup_drop_zone()**: Sets up the drag-and-drop area for images
- **_setup_format_selector()**: Creates the grid of available output formats
- **_setup_process_button()**: Adds the process and cancel buttons
- **_setup_progress_indicator()**: Creates the progress bar component
- **_apply_theme()**: Applies the HungerRush styling to all components

### 3. Input Handling
When the user provides an input file (either through the file browser or drag-and-drop):

- **_handle_file_drop()**: Updates the UI when a file is dropped
- **_browse_input_file()**: Opens a file dialog and handles selection
- **_browse_output_directory()**: Opens a directory dialog for output selection
- **update_input_path()**: Updates relevant UI components with the file path
- **_validate_inputs()**: Checks that all required inputs are valid before processing

### 4. Image Processing Initiation (`src/ui/main_window.py`)
When the user clicks "Process Images":

- **_process_images()**: Validates inputs and sets up processing
- **_start_processing_progress()**: Updates UI for processing state
- Creates worker thread (**ImageProcessingWorker**) to handle processing in background
- Sets up signal connections for progress updates and results handling

### 5. Image Processing Service (`src/services/image_processing_service.py`)
The main service coordinates the image processing:

- **process_batch()**: Processes multiple formats for a single input image
- **_process_single_format()**: Handles specific format processing
- Determines if background removal should be applied based on format and user selection
- Routes processing to appropriate specialized processors

### 6. Background Removal (`src/models/background_remover.py`)
If background removal is enabled, the following pipeline is applied:

- **remove_background()**: Main entry point for removal processing
- **detect_white_background()**: Determines if removal should be applied
- **_remove_with_combined_pipeline()**: Applies the full processing pipeline:
  1. **_contour_detection_method()**: Identifies object boundaries
  2. **_threshold_method()**: Creates binary mask using thresholding
  3. **_combine_masks()**: Merges results from both methods
  4. **_apply_morphological_operations()**: Cleans up the mask
  5. **_refine_contours()**: Further refines by focusing on significant areas
  6. **_final_cleanup()**: Performs final polish of the mask
  7. **_apply_transparency()**: Creates transparent image using the mask

### 7. Format-Specific Processing (`src/models/image_processor.py` and `src/models/push_processor.py`)
Different formats have specialized processing:
- **PushProcessor.create_push_notification()**: Creates white-on-transparent icons
- **ImageProcessor.process_logo()**: Special handling for logo formats
- **ImageProcessor.process_format()**: Generic format processing
- **ImageProcessor.process_image()**: Core image processing with resizing and positioning

### 8. Results Handling
When processing completes, results are returned to the UI:
- **_handle_processing_results()**: Processes and displays final status
- **_stop_processing_progress()**: Updates UI state back to ready
- Success or error messages are displayed to the user
- Processed images are saved to the specified output directory

## Key Classes and Functions

### Main Window (`src/ui/main_window.py`)
- **MainWindow**: Main application window with all UI components and event handling
  - **_validate_inputs()**: Checks input file, output directory, and selected formats
  - **_process_images()**: Initiates the image processing workflow
  - **_handle_processing_results()**: Processes final results and shows feedback

### Image Processing Service (`src/services/image_processing_service.py`)
- **ImageProcessingService**: Coordinates image processing operations
  - **process_batch()**: Processes an image into multiple formats
  - **process_single_format()**: Processes an image into a single format
  - **_convert_cv_to_pil()**: Converts OpenCV images to PIL format

### Background Remover (`src/models/background_remover.py`)
 - **BackgroundRemover**: Implements background removal pipeline
  - **remove_background()**: Removes background based on selected method
  - **detect_white_background()**: Detects if an image has a white background
  - **convert_to_white_icon()**: Converts an image to a white icon for PUSH format

### Image Processor (`src/models/image_processor.py`)
- **ImageProcessor**: Handles image resizing and format-specific processing
  - **process_image()**: Core resizing and positioning logic
  - **process_format()**: Processes an image for a specific predefined format
  - **process_logo()**: Special handling for logo formats (square and wide)

### Worker Thread (`src/utils/worker.py`)
- **ImageProcessingWorker**: Handles background processing to keep UI responsive
  - **process()**: Executes the image processing in a background thread
  - **cancel()**: Allows processing to be canceled
