import os
from pathlib import Path
from typing import List, Set, Union
import logging

logger = logging.getLogger(__name__)

# Define valid image formats
VALID_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.jfif'}

class FileUtils:
    """Utility functions for file handling, validation, and directory management."""

    @staticmethod
    def create_output_directory(path: Union[str, Path]) -> None:
        """
        Create a directory if it doesn't exist.

        Args:
            path (Union[str, Path]): The directory path to create.

        Raises:
            PermissionError: If permission is denied.
            Exception: If another error occurs while creating the directory.
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except PermissionError:
            msg = f"Permission denied while creating directory: {path}"
            logger.error(msg)
            raise PermissionError(msg)
        except Exception as e:
            msg = f"Error creating directory {path}: {e}"
            logger.error(msg)
            raise RuntimeError(msg)

    @staticmethod
    def validate_path(path: Union[str, Path], must_exist: bool = True) -> Path:
        """
        Validate file path existence and format.

        Args:
            path (Union[str, Path]): The file path to validate.
            must_exist (bool): If True, ensures the file exists.

        Returns:
            Path: Resolved valid file path.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file is not readable.
            ValueError: If the file format is not supported.
        """
        path = Path(path).resolve()

        if must_exist and not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if path.is_file():
            if not os.access(path, os.R_OK):
                raise PermissionError(f"No read permission: {path}")

            if path.suffix.lower() not in VALID_EXTENSIONS:
                raise ValueError(f"Invalid format: {path.suffix}. Supported formats: {', '.join(VALID_EXTENSIONS)}")

        return path

    @staticmethod
    def ensure_unique_path(path: Union[str, Path], pattern: str = "{name}_{index}{ext}") -> Path:
        """
        Generate a unique file path by appending an index if needed.

        Args:
            path (Union[str, Path]): The original file path.
            pattern (str): The pattern for renaming.

        Returns:
            Path: A unique path that does not already exist.
        """
        path = Path(path)
        if not path.exists():
            return path

        directory = path.parent
        name = path.stem
        ext = path.suffix
        index = 1

        while True:
            new_path = directory / pattern.format(name=name, index=index, ext=ext)
            if not new_path.exists():
                return new_path
            index += 1

    @staticmethod
    def list_image_files(directory: Union[str, Path]) -> List[Path]:
        """
        List all valid image files in a directory.

        Args:
            directory (Union[str, Path]): The directory to scan.

        Returns:
            List[Path]: List of valid image file paths.

        Raises:
            NotADirectoryError: If the provided path is not a directory.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        return [
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS
        ]
