"""User model for recipe value system."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .cooking_log import UserCookingHistory
from .enums import SkillLevel, UserRole, UserStatus
from .preferences import UserPreferences
from .profile import UserTasteProfile
from .recipe import Recipe
from .user_interactions import UserRecipeInteraction


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model representing a user in the system."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Basic information
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # User type and status
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLAlchemyEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE
    )
    skill_level: Mapped[Optional[SkillLevel]] = mapped_column(
        SQLAlchemyEnum(SkillLevel)
    )

    # Activity timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships - using string literals for forward references
    recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="author")
    interactions: Mapped[List["UserRecipeInteraction"]] = relationship(
        "UserRecipeInteraction", back_populates="user"
    )
    cooking_history: Mapped[List["UserCookingHistory"]] = relationship(
        "UserCookingHistory", back_populates="user"
    )
    preferences: Mapped["UserPreferences"] = relationship(
        "UserPreferences", back_populates="user", uselist=False
    )
    taste_profile: Mapped["UserTasteProfile"] = relationship(
        "UserTasteProfile", back_populates="user", uselist=False
    )

    def update_last_login(self) -> None:
        """Update the user's last login timestamp."""
        self.last_login_at = datetime.now(timezone.utc)

    def update_last_active(self) -> None:
        """Update the user's last active timestamp."""
        self.last_active_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "skill_level": self.skill_level.value if self.skill_level else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat()
            if self.last_login_at
            else None,
            "last_active_at": self.last_active_at.isoformat()
            if self.last_active_at
            else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "deleted_by_id": self.deleted_by_id,
        }
