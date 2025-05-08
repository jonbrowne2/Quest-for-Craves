"""Recipe models."""

from sqlalchemy import (
    JSON,
    Column,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .enums import DifficultyLevel, RecipeStatus


class Recipe(Base, TimestampMixin, SoftDeleteMixin):
    """Recipe model."""

    __tablename__ = "vault_recipes"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    source_url = Column(String(500))
    author = Column(String(100))
    image_url = Column(String(500))
    status = Column(
        Enum(RecipeStatus), nullable=False, default=RecipeStatus.PUBLISHED, index=True
    )

    # Recipe details
    description = Column(Text)
    ingredients = Column(JSON, nullable=False)  # List of ingredient objects
    instructions = Column(JSON, nullable=False)  # List of instruction steps
    equipment_needed = Column(JSON)  # List of required equipment
    serving_size = Column(Integer)
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    total_time = Column(Integer)

    # Nutrition
    calories_per_serving = Column(Integer)
    protein = Column(Float)  # grams
    carbs = Column(Float)  # grams
    fat = Column(Float)  # grams
    fiber = Column(Float)  # grams
    sugar = Column(Float)  # grams
    sodium = Column(Float)  # milligrams

    # Metadata
    cuisine_type = Column(String(50))
    meal_type = Column(String(50))  # breakfast, lunch, dinner, snack
    dish_type = Column(String(50))  # appetizer, main, side, dessert
    difficulty = Column(Enum(DifficultyLevel))
    tags = Column(JSON)  # List of tags
    dietary_info = Column(JSON)  # Dict of dietary information

    # Stats
    rating_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    favorite_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    cook_count = Column(Integer, default=0)

    # Value metrics
    difficulty_score = Column(Float)  # 1-5 scale
    complexity_score = Column(Float)  # 1-5 scale
    cost_per_serving = Column(Float)
    value_score = Column(Float)  # Overall value score

    # Relationships
    interactions = relationship(
        "UserRecipeInteraction",
        back_populates="recipe",
        foreign_keys="UserRecipeInteraction.recipe_id",
    )
    cooking_logs = relationship(
        "UserCookingHistory",
        back_populates="recipe",
        foreign_keys="UserCookingHistory.recipe_id",
    )
    recommendation_logs = relationship(
        "RecipeRecommendationLog",
        back_populates="recipe",
        foreign_keys="RecipeRecommendationLog.recipe_id",
    )

    __table_args__ = (
        # Composite indexes for common queries
        Index("ix_vault_recipes_rating_count", "average_rating", "rating_count"),
        Index("ix_vault_recipes_difficulty_time", "difficulty", "total_time"),
        Index("ix_vault_recipes_cuisine_rating", "cuisine_type", "average_rating"),
    )
