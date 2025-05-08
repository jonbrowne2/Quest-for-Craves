"""Recipe value calculation and tracking service."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Set

from ..analytics.business_insights import RecipeMetrics
from ..models.recipe import Recipe
from ..models.user_interactions import CookingHistory
from ..services.core.base_service import BaseService, ServiceStatus


@dataclass
class ValueMetrics:
    """Recipe value metrics."""

    quality_score: float = 0.0
    popularity_score: float = 0.0
    engagement_score: float = 0.0
    completion_rate: float = 0.0
    avg_cooking_time: Optional[int] = None
    total_cooks: int = 0
    successful_cooks: int = 0


@dataclass
class ValueCalculation:
    """Recipe value calculation result."""

    recipe_id: int
    base_value: Decimal
    quality_multiplier: float = 1.0
    popularity_multiplier: float = 1.0
    engagement_multiplier: float = 1.0
    seasonal_multiplier: float = 1.0
    final_value: Decimal = Decimal("0")
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RecipeValue:
    """Recipe value tracking."""

    recipe_id: int
    current_value: Decimal
    historical_values: List[ValueCalculation] = field(default_factory=list)
    metrics: ValueMetrics = field(default_factory=ValueMetrics)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ValueService(BaseService):
    """Service for calculating and tracking recipe values."""

    def __init__(self) -> None:
        """Initialize the value service."""
        super().__init__()
        self._recipe_values: Dict[int, RecipeValue] = {}
        self._recipe_metrics: Dict[int, RecipeMetrics] = {}
        self._base_values: Dict[str, Decimal] = {
            "easy": Decimal("5.00"),
            "medium": Decimal("7.50"),
            "hard": Decimal("10.00"),
        }

    def initialize(self) -> bool:
        """Initialize service and load required data."""
        try:
            # Load existing value data
            self._load_value_data()
            self._status = ServiceStatus(is_ready=True)
            return True
        except Exception as e:
            self._status = ServiceStatus(
                is_ready=False, error=f"Failed to initialize value service: {str(e)}"
            )
            return False

    def get_recipe_value(self, recipe_id: int) -> Optional[RecipeValue]:
        """Get current value and history for a recipe."""
        return self._recipe_values.get(recipe_id)

    def calculate_recipe_value(self, recipe: Recipe) -> Optional[RecipeValue]:
        """Calculate value for a recipe."""
        if not self._status.is_ready:
            return None

        try:
            # Get or create value tracking
            value = self._recipe_values.get(recipe.recipe_id)
            if not value:
                value = RecipeValue(
                    recipe_id=recipe.recipe_id, current_value=Decimal("0")
                )

            # Calculate new value
            calculation = self._calculate_value(recipe)

            # Update value tracking
            value.current_value = calculation.final_value
            value.historical_values.append(calculation)
            value.last_updated = datetime.utcnow()

            # Store updated value
            self._recipe_values[recipe.recipe_id] = value

            return value
        except Exception as e:
            self._status = ServiceStatus(
                is_ready=True, error=f"Failed to calculate recipe value: {str(e)}"
            )
            return None

    def update_recipe_metrics(
        self, recipe_id: int, cooking_history: List[CookingHistory]
    ) -> None:
        """Update recipe metrics based on cooking history."""
        if not cooking_history:
            return

        value = self._recipe_values.get(recipe_id)
        if not value:
            return

        metrics = value.metrics

        # Update completion metrics
        metrics.total_cooks = len(cooking_history)
        metrics.successful_cooks = sum(1 for h in cooking_history if h.completed)
        metrics.completion_rate = (
            metrics.successful_cooks / metrics.total_cooks
            if metrics.total_cooks > 0
            else 0.0
        )

        # Update cooking time
        cooking_times = [h.cooking_time for h in cooking_history if h.cooking_time]
        if cooking_times:
            metrics.avg_cooking_time = sum(cooking_times) // len(cooking_times)

        # Update engagement score (based on completion rate and cooking frequency)
        time_periods = len(set(h.cooked_at.date() for h in cooking_history))
        cooking_frequency = metrics.total_cooks / max(time_periods, 1)
        metrics.engagement_score = 0.7 * metrics.completion_rate + 0.3 * min(
            cooking_frequency, 1.0
        )

        # Update popularity score (based on total cooks and success rate)
        metrics.popularity_score = (
            0.6 * min(metrics.total_cooks / 100, 1.0)  # Cap at 100 cooks
            + 0.4 * metrics.completion_rate
        )

    def _calculate_value(self, recipe: Recipe) -> ValueCalculation:
        """Calculate recipe value with multipliers."""
        # Get base value from difficulty
        difficulty = recipe.difficulty_level or "medium"
        base_value = self._base_values.get(difficulty.lower(), Decimal("7.50"))

        calculation = ValueCalculation(
            recipe_id=recipe.recipe_id, base_value=base_value
        )

        # Get recipe metrics
        metrics = self._recipe_metrics.get(recipe.recipe_id)
        if metrics:
            calculation.quality_multiplier = max(0.5, metrics.overall_quality)

        # Get value metrics
        value = self._recipe_values.get(recipe.recipe_id)
        if value:
            calculation.popularity_multiplier = max(0.5, value.metrics.popularity_score)
            calculation.engagement_multiplier = max(0.5, value.metrics.engagement_score)

        # Calculate seasonal multiplier (placeholder)
        calculation.seasonal_multiplier = 1.0

        # Calculate final value
        calculation.final_value = (
            base_value
            * Decimal(str(calculation.quality_multiplier))
            * Decimal(str(calculation.popularity_multiplier))
            * Decimal(str(calculation.engagement_multiplier))
            * Decimal(str(calculation.seasonal_multiplier))
        ).quantize(Decimal("0.01"))

        return calculation

    def _load_value_data(self) -> None:
        """Load value data from database."""
        # TODO: Implement data loading from database
        pass
