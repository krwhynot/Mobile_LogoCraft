"""
Worker thread implementation for asynchronous image processing.
"""
from PySide6.QtCore import QObject, Signal, QThread
from pathlib import Path
import time

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    started = Signal()
    finished = Signal()
    error = Signal(str)
    progress = Signal(int, str)
    status = Signal(str, str)
    result = Signal(object)

class ImageProcessingWorker(QObject):
    """Worker thread for handling image processing tasks."""
    
    def __init__(self, processor, input_path, output_dir, formats, remove_background):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_dir = output_dir
        self.formats = formats
        self.remove_background = remove_background
        self.signals = WorkerSignals()
        self.is_cancelled = False
        
    def process(self):
        """Process all selected image formats in a separate thread."""
        try:
            self.signals.started.emit()
            self.signals.status.emit("Starting image processing...", "info")
            
            results = []
            total_formats = len(self.formats)
            
            # Create output directory if it doesn't exist
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Process each format
            for i, format_name in enumerate(self.formats):
                if self.is_cancelled:
                    break
                    
                # Update progress percentage and status
                progress_percent = int((i / total_formats) * 100)
                self.signals.progress.emit(progress_percent, f"Processing {format_name}...")
                
                # Process the current format
                result = self.processor.process_single_format(
                    self.input_path, 
                    self.output_dir, 
                    format_name, 
                    self.remove_background
                )
                
                # Add result to list
                results.append(result)
                
                # Small delay to ensure UI updates are visible
                QThread.msleep(50)
            
            # Final progress update
            self.signals.progress.emit(100, "Completed")
            self.signals.result.emit(results)
            self.signals.finished.emit()
            
        except Exception as e:
            self.signals.error.emit(str(e))
            self.signals.finished.emit()
    
    def cancel(self):
        """Cancel the current processing job."""
        self.is_cancelled = True
