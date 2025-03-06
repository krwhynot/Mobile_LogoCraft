class ImageProcessingError(Exception):
    """Exception raised for errors during image processing."""
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
