# This file will be executed by PyInstaller at startup
import os
import sys

# Patch the logging module's file handlers before any imports happen
def disable_logging_files():
    # Get the standard logging module
    import logging
    import logging.handlers
    
    # Create dummy handler classes that do nothing
    class DummyHandler(logging.Handler):
        def emit(self, record):
            pass
    
    # Replace all file-related handlers with our dummy handler
    logging.FileHandler = DummyHandler
    logging.handlers.RotatingFileHandler = DummyHandler
    logging.handlers.TimedRotatingFileHandler = DummyHandler
    
    # Make sure no log directory is created
    original_makedirs = os.makedirs
    
    def patched_makedirs(name, *args, **kwargs):
        # Prevent creation of directories with 'log' in the name
        if 'log' in name.lower():
            return
        return original_makedirs(name, *args, **kwargs)
    
    os.makedirs = patched_makedirs

# Run our patch function
disable_logging_files()
