"""Enums for the recipe value system."""

import enum


class TasteRating(enum.Enum):
    """User's taste rating for a recipe."""

    HATE = "hate"
    DONT_LIKE = "dont_like"
    MEH = "meh"
    LIKE = "like"
    LOVE = "love"
    CRAVE = "crave"


class DifficultyLevel(enum.Enum):
    """Recipe difficulty levels."""

    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    ADVANCED = "advanced"


class SkillLevel(enum.Enum):
    """User cooking skill levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class BudgetLevel(enum.Enum):
    """User budget preferences."""

    BUDGET = "budget"
    MODERATE = "moderate"
    PREMIUM = "premium"
    LUXURY = "luxury"


class SuccessLevel(enum.Enum):
    """Recipe cooking success levels."""

    FAILED = "failed"
    PARTIAL = "partial"
    SUCCESS = "success"
    PERFECT = "perfect"


class UserAction(enum.Enum):
    """User actions on recipes."""

    VIEW = "view"
    SAVE = "save"
    COOK = "cook"
    RATE = "rate"
    SHARE = "share"
    HIDE = "hide"


class InteractionType(enum.Enum):
    """Types of user interactions with recipes."""

    VIEW = "view"
    SAVE = "save"
    COOK = "cook"
    RATE = "rate"
    SHARE = "share"
    HIDE = "hide"


class RecipeStatus(enum.Enum):
    """
    Enumeration of recipe statuses.

    This enum defines the various statuses that can be assigned to a recipe.
    Statuses reflect the quality and significance of recipes, with 'legendary'
    being reserved for truly exceptional recipes that represent the best in their category.
    """

    DRAFT = "Draft"  # Recipe is still being developed/tested
    PUBLISHED = "Published"  # Basic published status
    VERIFIED = "Verified"  # Recipe has been tested and verified
    EXCELLENT = "Excellent"  # Recipe is highly rated and popular
    LEGENDARY = "Legendary"  # Reserved for the absolute best recipes
