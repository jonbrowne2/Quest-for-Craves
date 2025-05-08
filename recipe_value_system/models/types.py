"""Type definitions for recipe value system models."""

from typing import Any, Dict, List, Optional, TypedDict

# Basic type aliases
JsonDict = Dict[str, Any]


# Recipe-related type definitions
class IngredientDict(TypedDict):
    """Ingredient information."""

    name: str
    amount: float
    unit: str
    notes: Optional[str]


class InstructionDict(TypedDict):
    """Instruction information."""

    step: int
    text: str
    time: Optional[int]
    notes: Optional[str]


class RecipeMetrics(TypedDict):
    """Recipe metrics."""

    complexity: float  # 0-1 scale
    time_required: float  # minutes
    ingredient_cost: float  # estimated cost in USD
    nutrition_score: float  # 0-1 scale
    taste_score: float  # 0-1 scale
    popularity: float  # 0-1 scale


class NutritionInfo(TypedDict):
    """Nutrition information."""

    calories: float  # kcal
    protein: float  # grams
    carbohydrates: float  # grams
    fat: float  # grams
    fiber: float  # grams
    sugar: float  # grams
    sodium: float  # milligrams
    vitamins: Dict[str, float]  # % daily value
    minerals: Dict[str, float]  # % daily value


# User-related type definitions
class UserPreferenceDict(TypedDict):
    """User preference dictionary."""

    dietary_restrictions: List[str]
    dietary_preferences: List[str]
    disliked_ingredients: List[str]
    favorite_cuisines: List[str]
    preferred_cooking_time: Optional[int]
    household_size: Optional[int]


class TasteProfileDict(TypedDict):
    """User taste profile dictionary."""

    flavor_preferences: Dict[str, float]  # e.g., {'sweet': 0.8, 'spicy': 0.4}
    texture_preferences: Dict[str, float]
    cuisine_affinities: Dict[str, float]
    ingredient_affinities: Dict[str, float]
    seasonal_preferences: Dict[str, float]
