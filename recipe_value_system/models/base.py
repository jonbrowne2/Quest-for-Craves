"""Base models and mixins for recipe value system."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column

Base = declarative_base()


class TimestampMixin:
    """Timestamps."""

    created_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    """Soft delete."""

    deleted_at = mapped_column(DateTime(timezone=True))
    deleted_by_id = mapped_column(Integer)

    def soft_delete(self, user_id: Optional[int] = None) -> None:
        """Soft delete."""
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by_id = user_id

    def restore(self) -> None:
        """Restore."""
        self.deleted_at = None
        self.deleted_by_id = None

    @property
    def is_deleted(self) -> bool:
        """Check if deleted."""
        return self.deleted_at is not None
