"""
Base service for handling core functionalities.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


@dataclass
class ServiceStatus:
    """Service status information."""

    service_name: str
    status: str
    is_initialized: bool = False


class BaseService(ABC):
    """Base service class for handling common operations."""

    def __init__(self) -> None:
        """Initialize service with logging."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize service resources."""
        raise NotImplementedError

    def get_status(self) -> ServiceStatus:
        """Get current service status."""
        return ServiceStatus(
            service_name=self.__class__.__name__,
            status="active" if self._initialized else "inactive",
            is_initialized=self._initialized,
        )

    def shutdown(self) -> None:
        """Clean up service resources."""
        self.logger.info(f"Shutting down {self.__class__.__name__}")
        self._initialized = False
