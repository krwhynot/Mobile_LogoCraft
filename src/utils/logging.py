"""
Empty module to replace logging functionality.
This module provides dummy logging functionality that does nothing,
effectively disabling log file creation.
"""

class DummyLogger:
    """
    A dummy logger that doesn't create any log files.
    All logging methods are implemented as no-ops.
    """
    
    def __init__(self, name=None):
        self.name = name
    
    def debug(self, msg, *args, **kwargs):
        pass
    
    def info(self, msg, *args, **kwargs):
        pass
    
    def warning(self, msg, *args, **kwargs):
        pass
    
    def error(self, msg, *args, **kwargs):
        pass
    
    def critical(self, msg, *args, **kwargs):
        pass
    
    def exception(self, msg, *args, **kwargs):
        pass
    
    def log(self, level, msg, *args, **kwargs):
        pass


def get_logger(name=None):
    """
    Get a dummy logger instance that doesn't create any log files.
    
    Args:
        name: Ignored parameter for compatibility
        
    Returns:
        DummyLogger: A dummy logger that doesn't do anything
    """
    return DummyLogger(name)
