"""Models package for recipe value system."""

from .base import Base, TimestampMixin
from .enums import (
    BudgetLevel,
    CookingMethod,
    CuisineType,
    DifficultyLevel,
    InteractionType,
    MealType,
    RecipeCategory,
    RecipeStatus,
    SkillLevel,
    SuccessLevel,
    TasteRating,
    UserAction,
    UserRole,
    UserStatus,
)
from .recipe import Recipe
from .types import NutritionInfo, RecipeMetrics, RecipeStats, UserStats
from .user import User
from .user_interactions import (
    RecipeRecommendationLog,
    UserCookingHistory,
    UserPreferences,
    UserRecipeInteraction,
    UserTasteProfile,
)

__all__ = [
    # Base models
    "Base",
    "TimestampMixin",
    # Enums
    "BudgetLevel",
    "CookingMethod",
    "CuisineType",
    "DifficultyLevel",
    "InteractionType",
    "MealType",
    "RecipeCategory",
    "RecipeStatus",
    "SkillLevel",
    "SuccessLevel",
    "TasteRating",
    "UserAction",
    "UserRole",
    "UserStatus",
    # Models
    "Recipe",
    "User",
    "RecipeRecommendationLog",
    "UserCookingHistory",
    "UserPreferences",
    "UserRecipeInteraction",
    "UserTasteProfile",
    # Types
    "NutritionInfo",
    "RecipeMetrics",
    "RecipeStats",
    "UserStats",
]


def configure_mappers() -> None:
    """Configure SQLAlchemy mappers.

    This function should be called after all models are imported in your tests
    or main application to ensure proper configuration of SQLAlchemy mappers.
    """
    from sqlalchemy.orm import configure_mappers

    configure_mappers()
