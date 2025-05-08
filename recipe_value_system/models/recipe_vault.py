"""Recipe vault models."""

from enum import Enum

from sqlalchemy import JSON, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, MetaData, String

from .base import Base, SoftDeleteMixin, TimestampMixin

# Create metadata
metadata = MetaData()


class DifficultyLevel(str, Enum):
    """Difficulty levels for recipes."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class CuisineType(str, Enum):
    """Cuisine types for recipes."""

    AMERICAN = "AMERICAN"
    ITALIAN = "ITALIAN"
    CHINESE = "CHINESE"
    JAPANESE = "JAPANESE"
    MEXICAN = "MEXICAN"
    INDIAN = "INDIAN"
    FRENCH = "FRENCH"
    MEDITERRANEAN = "MEDITERRANEAN"
    OTHER = "OTHER"


class Recipe(Base, TimestampMixin, SoftDeleteMixin):
    """Recipe model for storing recipes in the vault.

    Attributes:
        id: Unique identifier for the recipe
        name: Name of the recipe
        ingredients: Ingredients required for the recipe
        instructions: Instructions for preparing the recipe
        nutritional_info: Nutritional information for the recipe
        cooking_time: Cooking time for the recipe in minutes
        difficulty_level: Difficulty level of the recipe
        cuisine_type: Cuisine type of the recipe
        dietary_restrictions: Dietary restrictions for the recipe
        dietary_preferences: Dietary preferences for the recipe
        estimated_cost: Estimated cost of the recipe
        serving_size: Serving size of the recipe
        flavor_profile: Flavor profile of the recipe
        texture_profile: Texture profile of the recipe
        seasonal_tags: Seasonal tags for the recipe
    """

    __tablename__ = "vault_recipes"
    __table_args__ = {"extend_existing": True}

    # Primary key
    id: int = Column(Integer, primary_key=True)

    # Basic recipe info
    name: str = Column(String, nullable=False)
    ingredients: dict = Column(JSON, nullable=False)
    instructions: list = Column(JSON, nullable=False)
    nutritional_info: dict = Column(JSON, nullable=False)
    cooking_time: int = Column(Integer)  # minutes
    difficulty_level: DifficultyLevel = Column(SQLEnum(DifficultyLevel))
    cuisine_type: CuisineType = Column(SQLEnum(CuisineType))
    dietary_restrictions: list = Column(JSON)
    dietary_preferences: list = Column(JSON)
    estimated_cost: float = Column(Float)
    serving_size: int = Column(Integer)

    # Metadata for recipe analysis
    flavor_profile: dict = Column(JSON)
    texture_profile: dict = Column(JSON)
    seasonal_tags: list = Column(JSON)
