"""Recipe analytics job module."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ...config.analytics_config import AnalyticsConfig
from ...models.recipe import Recipe
from ..analytics_service import AnalyticsService


class RecipeAnalyticsJob:
    """Job for running recipe analytics."""

    def __init__(
        self,
        session: Session,
        config: Optional[AnalyticsConfig] = None,
    ) -> None:
        """Initialize recipe analytics job.

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
        self.analytics_service = AnalyticsService(session, config)

    def run(self, recipes: Optional[List[Recipe]] = None) -> Dict[str, float]:
        """Run analytics job on recipes.

        Args:
            recipes: Optional list of recipes to analyze. If None, analyzes all recipes.

        Returns:
            Dictionary of aggregated metrics

        Raises:
            TypeError: If recipes contains non-Recipe objects
        """
        if recipes is None:
            recipes = self.session.query(Recipe).all()

        if not all(isinstance(recipe, Recipe) for recipe in recipes):
            raise TypeError("All elements in recipes must be of type Recipe")

        metrics: Dict[str, float] = {
            "total_recipes": len(recipes),
            "avg_quality": 0.0,
            "avg_complexity": 0.0,
            "avg_time_value": 0.0,
            "last_run": datetime.now().timestamp(),
        }

        for recipe in recipes:
            recipe_metrics = self.analytics_service.generate_value_metrics(recipe)
            metrics["avg_quality"] += recipe_metrics["quality_score"]
            metrics["avg_complexity"] += recipe_metrics["complexity_score"]
            metrics["avg_time_value"] += recipe_metrics["time_value_score"]

        if recipes:
            metrics["avg_quality"] /= len(recipes)
            metrics["avg_complexity"] /= len(recipes)
            metrics["avg_time_value"] /= len(recipes)

        return metrics
