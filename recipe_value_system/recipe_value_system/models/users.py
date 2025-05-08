"""User models."""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .enums import SkillLevel


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)

    # Profile
    display_name = Column(String(50))
    bio = Column(String(500))
    avatar_url = Column(String(200))
    skill_level = Column(Enum(SkillLevel))
    user_preferences = Column(JSON)  # General preferences

    # Stats
    recipe_count = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)

    # Relationships
    interactions = relationship(
        "UserRecipeInteraction",
        back_populates="user",
        foreign_keys="UserRecipeInteraction.user_id",
    )
    preferences = relationship(
        "UserPreferences", back_populates="user", foreign_keys="UserPreferences.user_id"
    )
    cooking_history = relationship(
        "UserCookingHistory",
        back_populates="user",
        foreign_keys="UserCookingHistory.user_id",
    )
    taste_profile = relationship(
        "UserTasteProfile",
        back_populates="user",
        foreign_keys="UserTasteProfile.user_id",
    )
    recommendation_logs = relationship(
        "RecipeRecommendationLog",
        back_populates="user",
        foreign_keys="RecipeRecommendationLog.user_id",
    )
