"""Module for defining the Recipe model and related functionality."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import JSON, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .cooking_log import UserCookingHistory
from .enums import (
    CookingMethod,
    CuisineType,
    DifficultyLevel,
    MealType,
    RecipeCategory,
    RecipeStatus,
)
from .recommendation import RecipeRecommendationLog
from .user import User
from .user_interactions import UserRecipeInteraction


class Recipe(Base, TimestampMixin):
    """Recipe model representing a cooking recipe in the system."""

    __tablename__ = "recipes"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Basic information
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    ingredients: Mapped[List[Dict]] = mapped_column(JSON, nullable=False)
    instructions: Mapped[List[Dict]] = mapped_column(JSON, nullable=False)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    # Timing information
    prep_time: Mapped[Optional[int]] = mapped_column(Integer)
    cook_time: Mapped[Optional[int]] = mapped_column(Integer)
    total_time: Mapped[Optional[int]] = mapped_column(Integer)
    servings: Mapped[Optional[int]] = mapped_column(Integer)

    # Classification
    difficulty: Mapped[Optional[DifficultyLevel]] = mapped_column(
        SQLAlchemyEnum(DifficultyLevel)
    )
    cuisine_type: Mapped[Optional[CuisineType]] = mapped_column(
        SQLAlchemyEnum(CuisineType), index=True
    )
    meal_type: Mapped[Optional[MealType]] = mapped_column(SQLAlchemyEnum(MealType))
    cooking_method: Mapped[Optional[CookingMethod]] = mapped_column(
        SQLAlchemyEnum(CookingMethod)
    )
    category: Mapped[Optional[RecipeCategory]] = mapped_column(
        SQLAlchemyEnum(RecipeCategory)
    )
    status: Mapped[RecipeStatus] = mapped_column(
        SQLAlchemyEnum(RecipeStatus),
        nullable=False,
        default=RecipeStatus.DRAFT,
        index=True,
    )

    # Nutritional information
    calories: Mapped[Optional[float]] = mapped_column(Float)
    protein: Mapped[Optional[float]] = mapped_column(Float)
    carbohydrates: Mapped[Optional[float]] = mapped_column(Float)
    fat: Mapped[Optional[float]] = mapped_column(Float)
    fiber: Mapped[Optional[float]] = mapped_column(Float)
    sugar: Mapped[Optional[float]] = mapped_column(Float)
    sodium: Mapped[Optional[float]] = mapped_column(Float)

    # Foreign keys
    author_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships - using string literals for forward references
    user_interactions: Mapped[List[UserRecipeInteraction]] = relationship(
        UserRecipeInteraction, back_populates="recipe"
    )
    cooking_history: Mapped[List[UserCookingHistory]] = relationship(
        UserCookingHistory, back_populates="recipe"
    )
    recommendations: Mapped[List[RecipeRecommendationLog]] = relationship(
        RecipeRecommendationLog, back_populates="recipe"
    )
    author: Mapped[Optional[User]] = relationship(User, back_populates="recipes")

    def to_dict(self) -> Dict:
        """Convert recipe to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "metadata": self.metadata,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "total_time": self.total_time,
            "servings": self.servings,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "cuisine_type": self.cuisine_type.value if self.cuisine_type else None,
            "meal_type": self.meal_type.value if self.meal_type else None,
            "cooking_method": self.cooking_method.value
            if self.cooking_method
            else None,
            "category": self.category.value if self.category else None,
            "status": self.status.value,
            "calories": self.calories,
            "protein": self.protein,
            "carbohydrates": self.carbohydrates,
            "fat": self.fat,
            "fiber": self.fiber,
            "sugar": self.sugar,
            "sodium": self.sodium,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __init__(self, title: str, ingredients: list, instructions: list) -> None:
        """Initialize a Recipe instance with title, ingredients, and instructions.

        Args:
            title: The recipe title.
            ingredients: List of ingredient details.
            instructions: List of cooking instructions.
        """
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
