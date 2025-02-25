"""
Dialog utility functions for the Mobile LogoCraft application.
Provides standardized message dialogs for user interaction.
"""
from PySide6.QtWidgets import QWidget, QMessageBox


def show_error(parent: QWidget, title: str, message: str) -> None:
    """
    Display an error message dialog.
    
    Args:
        parent: Parent widget for the dialog
        title: Dialog title
        message: Error message to display
    """
    QMessageBox.critical(parent, title, message)


def show_warning(parent: QWidget, title: str, message: str) -> None:
    """
    Display a warning message dialog.
    
    Args:
        parent: Parent widget for the dialog
        title: Dialog title
        message: Warning message to display
    """
    QMessageBox.warning(parent, title, message)


def show_info(parent: QWidget, title: str, message: str) -> None:
    """
    Display an information message dialog.
    
    Args:
        parent: Parent widget for the dialog
        title: Dialog title
        message: Information message to display
    """
    QMessageBox.information(parent, title, message)


def show_confirmation(parent: QWidget, title: str, message: str) -> bool:
    """
    Display a confirmation dialog and return the user's choice.
    
    Args:
        parent: Parent widget for the dialog
        title: Dialog title
        message: Question to ask the user
        
    Returns:
        True if the user confirmed, False otherwise
    """
    return QMessageBox.question(
        parent, 
        title, 
        message, 
        QMessageBox.Yes | QMessageBox.No
    ) == QMessageBox.Yes
