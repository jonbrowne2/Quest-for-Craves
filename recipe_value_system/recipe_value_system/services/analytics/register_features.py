"""Feature registration module for analytics."""

from typing import Dict, Optional

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base

from ..config.analytics_config import AnalyticsConfig
from ..models.recipe import Recipe
from .feature_catalog import FeatureCatalog


def register_recipe_features(
    session: Session,
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, bool]:
    """Register recipe features for analytics.

    Args:
        session: Database session
        config: Optional analytics configuration

    Returns:
        Dictionary mapping feature names to registration status

    Raises:
        TypeError: If session or config is of incorrect type
    """
    if not isinstance(session, Session):
        raise TypeError("Session must be of type Session")
    if config and not isinstance(config, AnalyticsConfig):
        raise TypeError("Config must be of type AnalyticsConfig or None")

    catalog = FeatureCatalog(session)
    config = config or AnalyticsConfig()

    features = {
        "recipe_complexity": catalog.register_feature(
            "recipe_complexity",
            "Recipe complexity score based on ingredients and steps",
            enabled=True,
        ),
        "recipe_quality": catalog.register_feature(
            "recipe_quality",
            "Recipe quality score based on completeness and detail",
            enabled=True,
        ),
        "recipe_time_value": catalog.register_feature(
            "recipe_time_value",
            "Recipe time value score based on prep and cook time",
            enabled=True,
        ),
    }

    recipes = session.query(Recipe).all()
    for recipe in recipes:
        if recipe.ingredients and recipe.instructions:
            catalog.track_feature_usage("recipe_complexity", recipe.id)
            catalog.track_feature_usage("recipe_quality", recipe.id)
        if recipe.prep_time and recipe.cook_time:
            catalog.track_feature_usage("recipe_time_value", recipe.id)

    return features


def register_initial_features(
    session: Session,
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, bool]:
    """Register core features for tracking.

    This function initializes the analytics system with our core feature set.
    Features are organized into categories:
    - Core: Essential features for basic functionality
    - Growth: New experimental features being tested
    - Premium: Features available to paid users
    - Legacy: Features in maintenance mode

    Args:
        session: Database session
        config: Optional analytics configuration

    Returns:
        Dictionary mapping feature names to registration status

    Raises:
        TypeError: If session or config is of incorrect type
    """
    if not isinstance(session, Session):
        raise TypeError("Session must be of type Session")
    if config and not isinstance(config, AnalyticsConfig):
        raise TypeError("Config must be of type AnalyticsConfig or None")

    catalog = FeatureCatalog(session)
    config = config or AnalyticsConfig()

    features = {}

    # Core features
    core_features = {
        "search": catalog.register_feature(
            "search",
            "Recipe search functionality",
            enabled=True,
        ),
        "filter": catalog.register_feature(
            "filter",
            "Recipe filtering by ingredients",
            enabled=True,
        ),
    }
    features.update(core_features)

    # Growth features
    growth_features = {
        "meal_planner": catalog.register_feature(
            "meal_planner",
            "Weekly meal planning assistant",
            enabled=True,
        ),
        "shopping_list": catalog.register_feature(
            "shopping_list",
            "Automated shopping list generator",
            enabled=True,
        ),
    }
    features.update(growth_features)

    # Premium features
    premium_features = {
        "nutrition": catalog.register_feature(
            "nutrition",
            "Detailed nutrition analysis",
            enabled=True,
        ),
        "recommendations": catalog.register_feature(
            "recommendations",
            "Personalized recipe recommendations",
            enabled=True,
        ),
    }
    features.update(premium_features)

    # Legacy features
    legacy_features = {
        "email_share": catalog.register_feature(
            "email_share",
            "Share recipes via email",
            enabled=True,
        ),
        "print": catalog.register_feature(
            "print",
            "Print recipe cards",
            enabled=True,
        ),
    }
    features.update(legacy_features)

    # Register recipe features
    recipe_features = register_recipe_features(session, config)
    features.update(recipe_features)

    return features


if __name__ == "__main__":
    engine = create_engine("sqlite:///example.db")
    Base = declarative_base()

    class TestRecipe(Base):
        """Recipe model for testing."""

        __tablename__ = "recipes"
        id = Column(Integer, primary_key=True)
        ingredients = Column(String)
        instructions = Column(String)
        prep_time = Column(Integer)
        cook_time = Column(Integer)

    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    config = AnalyticsConfig()
    register_initial_features(session, config)
