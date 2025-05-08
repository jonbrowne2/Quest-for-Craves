"""Enums for recipe value system."""

from enum import Enum


class UserRole(str, Enum):
    """User role enum."""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class UserStatus(str, Enum):
    """User status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class RecipeStatus(str, Enum):
    """Recipe status enum."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CuisineType(str, Enum):
    """Cuisine type enum."""

    AMERICAN = "american"
    CHINESE = "chinese"
    FRENCH = "french"
    INDIAN = "indian"
    ITALIAN = "italian"
    JAPANESE = "japanese"
    KOREAN = "korean"
    MEXICAN = "mexican"
    THAI = "thai"
    OTHER = "other"


class MealType(str, Enum):
    """Meal type enum."""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"


class DifficultyLevel(str, Enum):
    """Difficulty level enum."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CookingMethod(str, Enum):
    """Cooking method enum."""

    BAKE = "bake"
    BOIL = "boil"
    BROIL = "broil"
    FRY = "fry"
    GRILL = "grill"
    ROAST = "roast"
    SAUTE = "saute"
    STEAM = "steam"


class RecipeCategory(str, Enum):
    """Recipe category enum."""

    APPETIZER = "appetizer"
    MAIN = "main"
    SIDE = "side"
    SOUP = "soup"
    SALAD = "salad"
    DESSERT = "dessert"
    BEVERAGE = "beverage"


class InteractionType(str, Enum):
    """User interaction type enum."""

    VIEW = "view"
    SAVE = "save"
    COOK = "cook"
    RATE = "rate"


class TasteRating(str, Enum):
    """Taste rating enum."""

    HATE = "hate"
    DISLIKE = "dislike"
    NEUTRAL = "neutral"
    LIKE = "like"
    LOVE = "love"


class SuccessLevel(str, Enum):
    """Success level enum."""

    FAILED = "failed"
    PARTIAL = "partial"
    SUCCESS = "success"


class BudgetLevel(str, Enum):
    """Budget level enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkillLevel(str, Enum):
    """Skill level enum."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserAction(str, Enum):
    """User action enum."""

    VIEWED = "viewed"
    SAVED = "saved"
    COOKED = "cooked"
    RATED = "rated"
