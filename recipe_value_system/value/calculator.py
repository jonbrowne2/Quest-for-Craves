"""Value calculator module for recipe metrics."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
from numpy.typing import NDArray
from sqlalchemy.orm import Session

from ..config.analytics_config import AnalyticsConfig
from ..models.recipe import Recipe


class ValueMetrics:
    """Value metrics dictionary type."""

    quality: float
    complexity: float
    rating: float
    time_value: float


class ValueCalculator:
    """Calculator for recipe value metrics."""

    def __init__(
        self, session: Session, config: Optional[AnalyticsConfig] = None
    ) -> None:
        """Initialize value calculator.

        Args:
            session: Database session
            config: Optional analytics configuration
        """
        self.session = session
        self.config = config or AnalyticsConfig()

    def calculate_quality_score(self, recipe: Recipe) -> float:
        """Calculate recipe quality score.

        Args:
            recipe: Recipe to analyze

        Returns:
            Quality score between 0 and 1
        """
        if not recipe.rating:
            return 0.0

        base_score = recipe.rating / 5.0
        completeness = self._calculate_completeness(recipe)
        return min(1.0, base_score * completeness)

    def calculate_complexity_score(self, recipe: Recipe) -> float:
        """Calculate recipe complexity score.

        Args:
            recipe: Recipe to analyze

        Returns:
            Complexity score between 0 and 1
        """
        if not recipe.complexity:
            return 0.0

        return min(1.0, max(0.0, recipe.complexity))

    def calculate_time_value(self, recipe: Recipe) -> float:
        """Calculate recipe time value score.

        Args:
            recipe: Recipe to analyze

        Returns:
            Time value score between 0 and 1
        """
        total_time = recipe.get_total_time()
        if not total_time:
            return 0.0

        # Normalize time value (assuming 2 hours is maximum reasonable time)
        max_time = 120
        time_factor = 1.0 - min(1.0, total_time / max_time)
        return time_factor

    def calculate_rating_impact(self, recipe: Recipe) -> float:
        """Calculate recipe rating impact score.

        Args:
            recipe: Recipe to analyze

        Returns:
            Rating impact score between 0 and 1
        """
        if not recipe.rating:
            return 0.0

        base_impact = recipe.rating / 5.0
        time_factor = self.calculate_time_value(recipe)
        return min(1.0, base_impact * (1.0 + time_factor))

    def calculate_value_metrics(self, recipe: Recipe) -> ValueMetrics:
        """Calculate all value metrics for a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Dictionary of value metrics
        """
        return {
            "quality": self.calculate_quality_score(recipe),
            "complexity": self.calculate_complexity_score(recipe),
            "rating": self.calculate_rating_impact(recipe),
            "time_value": self.calculate_time_value(recipe),
        }

    def aggregate_metrics(self, metrics_list: List[ValueMetrics]) -> Dict[str, float]:
        """Aggregate multiple recipe metrics.

        Args:
            metrics_list: List of value metrics

        Returns:
            Dictionary of aggregated metrics
        """
        if not metrics_list:
            return {
                "quality_avg": 0.0,
                "complexity_avg": 0.0,
                "rating_avg": 0.0,
                "time_value_avg": 0.0,
            }

        metrics_array = np.array(
            [
                [
                    metrics["quality"],
                    metrics["complexity"],
                    metrics["rating"],
                    metrics["time_value"],
                ]
                for metrics in metrics_list
            ]
        )

        averages = np.mean(metrics_array, axis=0)
        return {
            "quality_avg": float(averages[0]),
            "complexity_avg": float(averages[1]),
            "rating_avg": float(averages[2]),
            "time_value_avg": float(averages[3]),
        }

    def analyze_trends(
        self, recipe: Recipe, window: timedelta = timedelta(days=30)
    ) -> Dict[str, NDArray[np.float64]]:
        """Analyze recipe metric trends over time.

        Args:
            recipe: Recipe to analyze
            window: Time window for trend analysis

        Returns:
            Dictionary of metric trends
        """
        cutoff_date = datetime.utcnow() - window
        historical_metrics = (
            self.session.query(Recipe)
            .filter(Recipe.id == recipe.id)
            .filter(Recipe.updated_at >= cutoff_date)
            .order_by(Recipe.updated_at)
            .all()
        )

        metrics_list = [self.calculate_value_metrics(r) for r in historical_metrics]
        if not metrics_list:
            return {
                "quality_trend": np.array([]),
                "complexity_trend": np.array([]),
                "rating_trend": np.array([]),
                "time_value_trend": np.array([]),
            }

        metrics_array = np.array(
            [
                [
                    metrics["quality"],
                    metrics["complexity"],
                    metrics["rating"],
                    metrics["time_value"],
                ]
                for metrics in metrics_list
            ]
        )

        return {
            "quality_trend": metrics_array[:, 0],
            "complexity_trend": metrics_array[:, 1],
            "rating_trend": metrics_array[:, 2],
            "time_value_trend": metrics_array[:, 3],
        }

    def compare_recipes(self, recipe1: Recipe, recipe2: Recipe) -> Dict[str, float]:
        """Compare two recipes based on their metrics.

        Args:
            recipe1: First recipe
            recipe2: Second recipe

        Returns:
            Dictionary of metric differences
        """
        metrics1 = self.calculate_value_metrics(recipe1)
        metrics2 = self.calculate_value_metrics(recipe2)

        return {
            "quality_diff": metrics1["quality"] - metrics2["quality"],
            "complexity_diff": metrics1["complexity"] - metrics2["complexity"],
            "rating_diff": metrics1["rating"] - metrics2["rating"],
            "time_value_diff": metrics1["time_value"] - metrics2["time_value"],
        }

    def calculate_value_distribution(self, recipes: List[Recipe]) -> Dict[str, float]:
        """Calculate value distribution across recipes.

        Args:
            recipes: List of recipes to analyze

        Returns:
            Dictionary of value distribution metrics
        """
        if not recipes:
            return {
                "quality_std": 0.0,
                "complexity_std": 0.0,
                "rating_std": 0.0,
                "time_value_std": 0.0,
            }

        metrics_list = [self.calculate_value_metrics(recipe) for recipe in recipes]
        metrics_array = np.array(
            [
                [
                    metrics["quality"],
                    metrics["complexity"],
                    metrics["rating"],
                    metrics["time_value"],
                ]
                for metrics in metrics_list
            ]
        )

        std_devs = np.std(metrics_array, axis=0)
        return {
            "quality_std": float(std_devs[0]),
            "complexity_std": float(std_devs[1]),
            "rating_std": float(std_devs[2]),
            "time_value_std": float(std_devs[3]),
        }

    def _calculate_completeness(self, recipe: Recipe) -> float:
        """Calculate recipe completeness score.

        Args:
            recipe: Recipe to analyze

        Returns:
            Completeness score between 0 and 1
        """
        required_fields = [
            recipe.description,
            recipe.prep_time,
            recipe.cook_time,
            recipe.complexity,
        ]
        filled_fields = sum(1 for field in required_fields if field is not None)
        return filled_fields / len(required_fields)
