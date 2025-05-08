"""Data export service module."""

from datetime import datetime
from typing import Dict, List, TypedDict, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sqlalchemy.orm import Session

from ..models.recipe import Recipe
from ..models.user import User
from ..value.calculator import ValueCalculator


class ExportMetrics(TypedDict):
    """Export metrics dictionary type."""

    quality: float
    complexity: float
    rating: float
    time_value: float
    total_recipes: int
    export_time: str


class DataExporter:
    """Service for exporting recipe and user data."""

    def __init__(self, session: Session) -> None:
        """Initialize data exporter.

        Args:
            session: Database session
        """
        self.session = session
        self.calculator = ValueCalculator(session)

    def export_recipe_metrics(self, recipe: Recipe) -> ExportMetrics:
        """Export metrics for a single recipe.

        Args:
            recipe: Recipe to export metrics for

        Returns:
            Dictionary of recipe metrics
        """
        metrics = self.calculator.calculate_value_metrics(recipe)
        return {
            "quality": metrics["quality"],
            "complexity": metrics["complexity"],
            "rating": metrics["rating"],
            "time_value": metrics["time_value"],
            "total_recipes": 1,
            "export_time": datetime.utcnow().isoformat(),
        }

    def export_user_recipes(self, user: User) -> pd.DataFrame:
        """Export all recipes for a user.

        Args:
            user: User to export recipes for

        Returns:
            DataFrame containing recipe data
        """
        recipes = user.recipes.all()
        recipe_data = []
        for recipe in recipes:
            metrics = self.calculator.calculate_value_metrics(recipe)
            recipe_data.append(
                {
                    "recipe_id": recipe.id,
                    "name": recipe.name,
                    "quality": metrics["quality"],
                    "complexity": metrics["complexity"],
                    "rating": metrics["rating"],
                    "time_value": metrics["time_value"],
                    "created_at": recipe.created_at,
                    "updated_at": recipe.updated_at,
                }
            )
        return pd.DataFrame(recipe_data)

    def export_recipe_trends(
        self, recipes: List[Recipe]
    ) -> Dict[str, NDArray[np.float64]]:
        """Export trend data for multiple recipes.

        Args:
            recipes: List of recipes to analyze

        Returns:
            Dictionary of trend arrays
        """
        metrics_list = [
            self.calculator.calculate_value_metrics(recipe) for recipe in recipes
        ]
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

    def export_recipe_distribution(self, recipes: List[Recipe]) -> Dict[str, float]:
        """Export value distribution across recipes.

        Args:
            recipes: List of recipes to analyze

        Returns:
            Dictionary of distribution metrics
        """
        return self.calculator.calculate_value_distribution(recipes)

    def export_user_stats(self, user: User) -> Dict[str, Union[int, float]]:
        """Export statistics for a user.

        Args:
            user: User to export statistics for

        Returns:
            Dictionary of user statistics
        """
        recipes = user.recipes.all()
        if not recipes:
            return {
                "total_recipes": 0,
                "avg_quality": 0.0,
                "avg_complexity": 0.0,
                "avg_rating": 0.0,
                "avg_time_value": 0.0,
            }

        metrics_list = [
            self.calculator.calculate_value_metrics(recipe) for recipe in recipes
        ]
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
            "total_recipes": len(recipes),
            "avg_quality": float(averages[0]),
            "avg_complexity": float(averages[1]),
            "avg_rating": float(averages[2]),
            "avg_time_value": float(averages[3]),
        }
