"""Models for user interactions with recipes."""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .enums import (
    BudgetLevel,
    DifficultyLevel,
    InteractionType,
    SkillLevel,
    SuccessLevel,
    TasteRating,
    UserAction,
)


class UserRecipeInteraction(Base, TimestampMixin):
    __tablename__ = "user_recipe_interactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("vault_recipes.id"), nullable=False)
    interaction_type = Column(Enum(InteractionType))  # VIEW, SAVE, COOK, RATE
    taste_rating = Column(Enum(TasteRating))  # Hate to Crave scale
    cooking_time_actual = Column(Integer)  # minutes
    difficulty_reported = Column(Enum(DifficultyLevel))
    notes = Column(Text)

    # Detailed feedback
    texture_rating = Column(Float)  # 1-5 scale
    appearance_rating = Column(Float)  # 1-5 scale
    would_cook_again = Column(Boolean)
    modifications_made = Column(JSON)

    # Relationships
    user = relationship("User", back_populates="interactions")
    recipe = relationship("Recipe", back_populates="interactions")


class UserPreferences(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dietary_restrictions = Column(JSON)
    dietary_preferences = Column(JSON)
    disliked_ingredients = Column(JSON)
    favorite_cuisines = Column(JSON)
    cooking_skill_level = Column(Enum(SkillLevel))
    preferred_cooking_time = Column(Integer)  # minutes
    household_size = Column(Integer)
    budget_preference = Column(Enum(BudgetLevel))

    # Relationships
    user = relationship("User", back_populates="preferences")


class UserCookingHistory(Base, TimestampMixin):
    __tablename__ = "user_cooking_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("vault_recipes.id"), nullable=False)
    cooked_at = Column(DateTime, nullable=False)
    success_level = Column(Enum(SuccessLevel))
    modifications = Column(JSON)
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="cooking_history")
    recipe = relationship("Recipe", back_populates="cooking_logs")


class UserTasteProfile(Base, TimestampMixin):
    __tablename__ = "user_taste_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flavor_preferences = Column(JSON)  # e.g., {'sweet': 0.8, 'spicy': 0.4}
    texture_preferences = Column(JSON)
    cuisine_affinities = Column(JSON)
    ingredient_affinities = Column(JSON)
    seasonal_preferences = Column(JSON)

    # Relationships
    user = relationship("User", back_populates="taste_profile")


class RecipeRecommendationLog(Base, TimestampMixin):
    __tablename__ = "recipe_recommendation_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("vault_recipes.id"), nullable=False)
    recommendation_score = Column(Float)
    recommendation_factors = Column(JSON)  # Why was this recommended
    user_action = Column(
        Enum(UserAction)
    )  # What did the user do with the recommendation
    context = Column(JSON)  # Time of day, season, etc.

    # Relationships
    user = relationship("User", back_populates="recommendation_logs")
    recipe = relationship("Recipe", back_populates="recommendation_logs")
