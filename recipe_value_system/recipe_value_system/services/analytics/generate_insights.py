"""Generate insights module for recipe analytics."""

from typing import Dict, Optional

import numpy as np
from sqlalchemy.orm import Session

from ..config.analytics_config import AnalyticsConfig
from ..models.recipe import Recipe
from .feature_catalog import FeatureCatalog


class InsightGenerator:
    """Generator for recipe analytics insights."""

    def __init__(
        self,
        session: Session,
        config: Optional[AnalyticsConfig] = None,
    ) -> None:
        """Initialize insight generator.

        Args:
            session: Database session
            config: Optional analytics configuration

        Raises:
            TypeError: If session or config is of incorrect type
        """
        if not isinstance(session, Session):
            raise TypeError("Session must be of type Session")
        if config and not isinstance(config, AnalyticsConfig):
            raise TypeError("Config must be of type AnalyticsConfig or None")

        self.session = session
        self.config = config or AnalyticsConfig()
        self.feature_catalog = FeatureCatalog(session)

    def generate_value_metrics(self, recipe: Recipe) -> Dict[str, float]:
        """Generate value metrics for a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Dictionary of value metrics

        Raises:
            TypeError: If recipe is of incorrect type
        """
        if not isinstance(recipe, Recipe):
            raise TypeError("Recipe must be of type Recipe")

        metrics: Dict[str, float] = {}
        metrics["quality_score"] = self._calculate_quality_score(recipe)
        metrics["complexity_score"] = self._calculate_complexity_score(recipe)
        metrics["time_value_score"] = self._calculate_time_value_score(recipe)
        return metrics

    def _calculate_quality_score(self, recipe: Recipe) -> float:
        """Calculate quality score for a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Quality score between 0 and 1

        Raises:
            TypeError: If recipe is of incorrect type
        """
        if not isinstance(recipe, Recipe):
            raise TypeError("Recipe must be of type Recipe")

        if not recipe.ingredients or not recipe.instructions:
            return 0.0

        ingredient_score = min(1.0, len(recipe.ingredients) / 10.0)
        instruction_score = min(1.0, len(recipe.instructions) / 15.0)
        return np.mean([ingredient_score, instruction_score])

    def _calculate_complexity_score(self, recipe: Recipe) -> float:
        """Calculate complexity score for a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Complexity score between 0 and 1

        Raises:
            TypeError: If recipe is of incorrect type
        """
        if not isinstance(recipe, Recipe):
            raise TypeError("Recipe must be of type Recipe")

        if not recipe.ingredients or not recipe.instructions:
            return 0.0

        ingredient_complexity = min(1.0, len(recipe.ingredients) / 20.0)
        instruction_complexity = min(1.0, len(recipe.instructions) / 30.0)
        return np.mean([ingredient_complexity, instruction_complexity])

    def _calculate_time_value_score(self, recipe: Recipe) -> float:
        """Calculate time value score for a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Time value score between 0 and 1

        Raises:
            TypeError: If recipe is of incorrect type
        """
        if not isinstance(recipe, Recipe):
            raise TypeError("Recipe must be of type Recipe")

        if not recipe.prep_time or not recipe.cook_time:
            return 0.0

        total_time = recipe.prep_time + recipe.cook_time
        time_score = 1.0 - min(1.0, total_time / 180.0)  # Cap at 3 hours
        return time_score
