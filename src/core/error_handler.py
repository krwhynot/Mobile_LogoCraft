import logging

logger = logging.getLogger(__name__)

class ImageProcessingError(Exception):
    """Exception raised for errors during image processing."""
    def __init__(self, message: str, *args):
        super().__init__(message, *args)
        self.message = message

class ValidationError(ImageProcessingError):
    """Exception raised when image validation fails."""
    pass

class ConfigurationError(Exception):
    """Exception raised for issues with loading or saving configurations."""
    pass

class FileProcessingError(Exception):
    """Exception raised for file-related issues (e.g., missing, permission errors)."""
    def __init__(self, message: str, *args):
        super().__init__(message, *args)
        self.message = message

def format_error(error: Exception) -> str:
    """
    Format error message for better debugging and logging.

    Args:
        error (Exception): The raised exception.

    Returns:
        str: Formatted error message.
    """
    if hasattr(error, 'message'):
        return f"[{error.__class__.__name__}] {error.message}"
    return f"[{error.__class__.__name__}] {str(error)}"

def log_error(error: Exception) -> None:
    """
    Log errors using the standard logging system.

    Args:
        error (Exception): The raised exception.
    """
    logger.error(format_error(error))
