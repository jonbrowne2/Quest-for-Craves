"""Type-safe error handling system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union

from ...config.settings import settings


@dataclass
class ErrorContext:
    """Context information for error tracking."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    service_name: Optional[str] = None
    operation: Optional[str] = None
    user_id: Optional[int] = None
    recipe_id: Optional[int] = None
    additional_data: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceError:
    """Base class for service errors."""

    message: str
    code: str
    context: ErrorContext
    severity: str = "error"  # error, warning, critical
    retry_count: int = 0
    max_retries: int = 3
    is_recoverable: bool = True

    def should_retry(self) -> bool:
        """Check if operation should be retried."""
        return (
            self.is_recoverable
            and self.retry_count < self.max_retries
            and self.severity != "critical"
        )


@dataclass
class DatabaseError(ServiceError):
    """Database-related errors."""

    table_name: Optional[str] = None
    operation_type: Optional[str] = None  # select, insert, update, delete


@dataclass
class ValidationError(ServiceError):
    """Data validation errors."""

    field_errors: Dict[str, List[str]] = field(default_factory=dict)
    invalid_value: Optional[str] = None


@dataclass
class BusinessLogicError(ServiceError):
    """Business rule violation errors."""

    rule_name: Optional[str] = None
    expected_value: Optional[Union[str, int, float]] = None
    actual_value: Optional[Union[str, int, float]] = None


class ErrorHandler:
    """Centralized error handling system."""

    def __init__(self) -> None:
        """Initialize error handler."""
        self._errors: List[ServiceError] = []
        self._error_counts: Dict[str, int] = {}

    def handle_error(self, error: ServiceError, raise_exception: bool = False) -> None:
        """Handle and log service error."""
        # Track error
        self._errors.append(error)

        # Update error counts
        error_key = f"{error.code}:{error.severity}"
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1

        # Log error with context
        self._log_error(error)

        # Handle based on severity
        if error.severity == "critical":
            self._handle_critical_error(error)
        elif error.severity == "error":
            self._handle_standard_error(error)
        else:  # warning
            self._handle_warning(error)

        if raise_exception:
            raise ValueError(f"{error.code}: {error.message}")

    def get_recent_errors(
        self,
        service_name: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 10,
    ) -> List[ServiceError]:
        """Get recent errors with optional filtering."""
        filtered = self._errors

        if service_name:
            filtered = [e for e in filtered if e.context.service_name == service_name]

        if severity:
            filtered = [e for e in filtered if e.severity == severity]

        return filtered[-limit:]

    def clear_errors(self) -> None:
        """Clear error history."""
        self._errors.clear()
        self._error_counts.clear()

    def _log_error(self, error: ServiceError) -> None:
        """Log error with appropriate level and context."""
        import logging

        logger = logging.getLogger(settings.app_name)

        log_message = (
            f"Error: {error.code} - {error.message}\n"
            f"Service: {error.context.service_name}\n"
            f"Operation: {error.context.operation}\n"
            f"Timestamp: {error.context.timestamp}\n"
            f"Severity: {error.severity}\n"
            f"Additional Data: {error.context.additional_data}"
        )

        if error.severity == "critical":
            logger.critical(log_message)
        elif error.severity == "error":
            logger.error(log_message)
        else:
            logger.warning(log_message)

    def _handle_critical_error(self, error: ServiceError) -> None:
        """Handle critical errors."""
        # Notify administrators
        self._notify_admin(error)

        # Log to special critical error file
        self._log_critical_error(error)

    def _handle_standard_error(self, error: ServiceError) -> None:
        """Handle standard errors."""
        if error.should_retry():
            # Implement retry logic
            pass

    def _handle_warning(self, error: ServiceError) -> None:
        """Handle warning level errors."""
        # Track warning patterns
        pass

    def _notify_admin(self, error: ServiceError) -> None:
        """Notify administrators of critical errors."""
        # TODO: Implement admin notification
        pass

    def _log_critical_error(self, error: ServiceError) -> None:
        """Log critical errors to separate file."""
        # TODO: Implement critical error logging
        pass


# Global error handler instance
error_handler = ErrorHandler()
