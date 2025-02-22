"""
Centralized logging configuration using a singleton pattern.
Provides consistent logging across the application with both file and console output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from functools import lru_cache

class LoggerSingleton:
    """
    Singleton class to manage logging configuration across the application.
    Ensures consistent logging format and handling across all modules.
    """
    
    _instance: Optional['LoggerSingleton'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'LoggerSingleton':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            LoggerSingleton._initialized = True
    
    def _setup_logging(self):
        """Configure logging with both file and console handlers."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
        
        # Define formatters for different outputs
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File Handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        root_logger.handlers = []
        
        # Add our handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

@lru_cache(maxsize=None)
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    Uses lru_cache to ensure the same logger instance is returned for the same name.
    
    Args:
        name: The name of the logger, typically __name__ from the calling module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Initialize the singleton to ensure logging is configured
    LoggerSingleton()
    
    # Get and return the logger
    logger = logging.getLogger(name)
    
    # Prevent duplicate logging by stopping propagation if this logger
    # has its own handlers
    if logger.handlers:
        logger.propagate = False
    
    return logger

# Example usage in other files:
# from src.utils.logging import get_logger
# logger = get_logger(__name__)