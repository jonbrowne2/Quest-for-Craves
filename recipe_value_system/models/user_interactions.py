"""User interaction models for recipe value system."""

from datetime import timezone
from typing import Dict, List, Optional

from sqlalchemy import JSON, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .enums import BudgetLevel, InteractionType, SuccessLevel, TasteRating


class UserRecipeInteraction(Base, TimestampMixin):
    """User interaction with a recipe."""

    __tablename__ = "user_recipe_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    interaction_type: Mapped[InteractionType] = mapped_column(
        SQLAlchemyEnum(InteractionType), nullable=False
    )
    rating: Mapped[Optional[TasteRating]] = mapped_column(SQLAlchemyEnum(TasteRating))
    notes: Mapped[Optional[str]] = mapped_column(JSON)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="interactions")
    recipe: Mapped["Recipe"] = relationship(
        "Recipe", back_populates="user_interactions"
    )


class UserCookingHistory(Base, TimestampMixin):
    """User's cooking history for a recipe."""

    __tablename__ = "user_cooking_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    success_level: Mapped[SuccessLevel] = mapped_column(
        SQLAlchemyEnum(SuccessLevel), nullable=False
    )
    cooking_time: Mapped[Optional[int]] = mapped_column(Integer)
    servings: Mapped[Optional[int]] = mapped_column(Integer)
    substitutions: Mapped[Optional[Dict]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(JSON)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="cooking_history")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="cooking_history")


class UserPreferences(Base, TimestampMixin):
    """User's cooking preferences."""

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    budget_level: Mapped[Optional[BudgetLevel]] = mapped_column(
        SQLAlchemyEnum(BudgetLevel)
    )
    max_cooking_time: Mapped[Optional[int]] = mapped_column(Integer)
    household_size: Mapped[Optional[int]] = mapped_column(Integer)
    preferences: Mapped[Dict] = mapped_column(JSON, nullable=False)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="preferences")


class UserTasteProfile(Base, TimestampMixin):
    """User's taste profile."""

    __tablename__ = "user_taste_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    profile: Mapped[Dict] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="taste_profile")


class RecipeRecommendationLog(Base, TimestampMixin):
    """Log of recipe recommendations made to users."""

    __tablename__ = "recipe_recommendation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    features: Mapped[Dict] = mapped_column(JSON, nullable=False)
    clicked: Mapped[bool] = mapped_column(nullable=False, default=False)
    cooked: Mapped[bool] = mapped_column(nullable=False, default=False)
    rated: Mapped[bool] = mapped_column(nullable=False, default=False)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recommendations")
