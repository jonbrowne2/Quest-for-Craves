"""
Base exporter class for handling data exports.

This module provides the base functionalities for all data exporters.
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")  # Type variable for the data being exported


class BaseExporter(ABC, Generic[T]):
    """
    Abstract base class for all data exporters.

    This class defines the common interface and utility methods that all
    concrete exporters must implement.

    Attributes:
        logger (logging.Logger): Logger instance for this exporter.
        output_dir (Path): Directory where exported files will be saved.
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize the base exporter.

        Args:
            output_dir: Directory where exported files will be saved.
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir) if output_dir else Path("exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(self, data: T, output_path: Union[str, Path], **kwargs: Any) -> Path:
        """
        Export data to the specified format.

        Args:
            data: The data to export.
            output_path: Path where the exported file will be saved.
            **kwargs: Additional format-specific parameters.

        Returns:
            Path: Path to the exported file.
        """
        raise NotImplementedError

    def validate_output_path(
        self, output_path: Union[str, Path], extension: Optional[str] = None
    ) -> Path:
        """
        Validate and normalize the output path.

        Args:
            output_path: The output path to validate.
            extension: File extension to ensure (without the dot).

        Returns:
            Path: Normalized Path object.
        """
        # Convert to Path object if it's a string
        path = Path(output_path)

        # If path is relative, make it relative to output_dir
        if not path.is_absolute():
            path = self.output_dir / path

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure the correct extension if specified
        if extension:
            if not extension.startswith("."):
                extension = f".{extension}"

            if not str(path).lower().endswith(extension.lower()):
                path = Path(f"{path}{extension}")

        return path

    def _ensure_parent_dir(self, path: Path) -> None:
        """
        Ensure the parent directory exists.

        Args:
            path: Path whose parent directory should exist.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

    def get_default_filename(self, prefix: str, extension: str) -> str:
        """
        Generate a default filename with timestamp.

        Args:
            prefix: Prefix for the filename.
            extension: File extension (without the dot).

        Returns:
            str: Formatted filename with timestamp.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not extension.startswith("."):
            extension = f".{extension}"

        return f"{prefix}_{timestamp}{extension}"
