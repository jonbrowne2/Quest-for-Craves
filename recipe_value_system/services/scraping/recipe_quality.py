"""High-quality recipe scraper and validator."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .cooking_data import (
    ALL_COOKING_METHODS,
    ALL_EQUIPMENT,
    ALL_INGREDIENTS,
    is_valid_serving_size,
    is_valid_temperature,
    is_valid_time,
    normalize_unit,
)


@dataclass
class RecipeMetrics:
    """Recipe quality evaluation metrics."""

    completeness_score: float = 0.0
    instruction_clarity: float = 0.0
    ingredient_validity: float = 0.0
    timing_validity: float = 0.0
    temperature_validity: float = 0.0
    portion_consistency: float = 0.0
    overall_quality: float = 0.0

    @property
    def is_high_quality(self) -> bool:
        """Check if recipe meets quality standards."""
        return (
            self.overall_quality >= 0.6
            and self.completeness_score >= 0.7
            and self.instruction_clarity >= 0.6
            and self.ingredient_validity >= 0.6
        )


@dataclass
class Ingredient:
    """Structured ingredient data."""

    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    preparation: Optional[str] = None


@dataclass
class Instruction:
    """Structured instruction step."""

    text: str
    duration: Optional[int] = None
    temperature: Optional[int] = None
    equipment: List[str] = field(default_factory=list)
    ingredients: List[str] = field(default_factory=list)


@dataclass
class RecipeYield:
    """Recipe yield information."""

    servings: int
    unit: str = "servings"
    notes: Optional[str] = None


@dataclass
class NutritionInfo:
    """Recipe nutritional information."""

    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None


@dataclass
class Recipe:
    """Structured recipe data with quality metrics."""

    title: str
    ingredients: List[Ingredient] = field(default_factory=list)
    instructions: List[Instruction] = field(default_factory=list)
    source_url: Optional[str] = None
    source_text: Optional[str] = None
    author: Optional[str] = None
    date_published: Optional[datetime] = None
    yields: Optional[RecipeYield] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    equipment: List[str] = field(default_factory=list)
    difficulty_level: Optional[str] = None
    cuisine_type: Optional[str] = None
    diet_categories: List[str] = field(default_factory=list)
    nutrition: NutritionInfo = field(default_factory=NutritionInfo)
    metrics: RecipeMetrics = field(default_factory=RecipeMetrics)
    source_attribution: str = "Unknown Source"
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def is_complete(self) -> bool:
        """Check if recipe has required components."""
        return bool(self.title and self.ingredients and self.instructions)


class RecipeQualityAnalyzer:
    """Service for assessing recipe quality."""

    def __init__(self) -> None:
        """Initialize analyzer with cooking knowledge."""
        self.common_ingredients = ALL_INGREDIENTS
        self.common_equipment = ALL_EQUIPMENT
        self.cooking_methods = ALL_COOKING_METHODS

    def analyze_recipe(self, recipe: Recipe) -> RecipeMetrics:
        """Analyze recipe and return quality metrics."""
        metrics = RecipeMetrics()

        metrics.completeness_score = self._check_completeness(recipe)
        metrics.instruction_clarity = self._check_instruction_clarity(recipe)
        metrics.ingredient_validity = self._check_ingredient_validity(recipe)
        metrics.timing_validity = self._check_timing_validity(recipe)
        metrics.temperature_validity = self._check_temperature_validity(recipe)
        metrics.portion_consistency = self._check_portion_consistency(recipe)

        weights = {
            "completeness": 0.25,
            "clarity": 0.25,
            "ingredients": 0.2,
            "timing": 0.1,
            "temperature": 0.1,
            "portions": 0.1,
        }

        metrics.overall_quality = (
            weights["completeness"] * metrics.completeness_score
            + weights["clarity"] * metrics.instruction_clarity
            + weights["ingredients"] * metrics.ingredient_validity
            + weights["timing"] * metrics.timing_validity
            + weights["temperature"] * metrics.temperature_validity
            + weights["portions"] * metrics.portion_consistency
        )

        return metrics

    def _check_completeness(self, recipe: Recipe) -> float:
        """Check recipe completeness with weighted components."""
        weights = {"title": 0.1, "ingredients": 0.4, "instructions": 0.4, "yields": 0.1}

        score = 0.0
        if recipe.title:
            score += weights["title"]
        if recipe.ingredients:
            score += weights["ingredients"] * min(1.0, len(recipe.ingredients) / 3)
        if recipe.instructions:
            score += weights["instructions"] * min(1.0, len(recipe.instructions) / 3)
        if recipe.yields:
            score += weights["yields"]

        return score

    def _check_instruction_clarity(self, recipe: Recipe) -> float:
        """Check instruction clarity and detail."""
        if not recipe.instructions:
            return 0.0

        total_score = 0.0
        for instruction in recipe.instructions:
            text = instruction.text.lower()
            if not text:
                continue

            # Check for cooking method clarity
            has_method = any(method in text for method in self.cooking_methods)

            # Check for timing information
            has_timing = instruction.duration is not None or any(
                time_word in text for time_word in ["minute", "hour", "until", "when"]
            )

            # Check for equipment mentions
            has_equipment = bool(instruction.equipment) or any(
                equip in text for equip in self.common_equipment
            )

            # Calculate step score
            step_score = (has_method + has_timing + has_equipment) / 3
            total_score += step_score

        return min(1.0, total_score / len(recipe.instructions))

    def _check_ingredient_validity(self, recipe: Recipe) -> float:
        """Check ingredient list validity."""
        if not recipe.ingredients:
            return 0.0

        valid_count = 0
        for ingredient in recipe.ingredients:
            # Check if ingredient name is recognized
            name_valid = any(
                known in ingredient.name.lower() for known in self.common_ingredients
            )

            # Check if amount and unit are present and valid
            measurement_valid = (
                ingredient.amount is not None
                and ingredient.unit is not None
                and normalize_unit(ingredient.unit) is not None
            )

            if name_valid and measurement_valid:
                valid_count += 1

        return valid_count / len(recipe.ingredients)

    def _check_timing_validity(self, recipe: Recipe) -> float:
        """Check cooking time reasonableness."""
        if not recipe.prep_time and not recipe.cook_time:
            return 0.0

        valid_times = 0
        total_checks = 0

        if recipe.prep_time is not None:
            total_checks += 1
            if is_valid_time(recipe.prep_time, "prep"):
                valid_times += 1

        if recipe.cook_time is not None:
            total_checks += 1
            if is_valid_time(recipe.cook_time, "cook"):
                valid_times += 1

        if recipe.total_time is not None:
            total_checks += 1
            expected_total = (recipe.prep_time or 0) + (recipe.cook_time or 0)
            if abs(recipe.total_time - expected_total) <= 10:  # 10 minute tolerance
                valid_times += 1

        return valid_times / total_checks if total_checks > 0 else 0.0

    def _check_temperature_validity(self, recipe: Recipe) -> float:
        """Check cooking temperature reasonableness."""
        temp_mentions = 0
        valid_temps = 0

        for instruction in recipe.instructions:
            if instruction.temperature is not None:
                temp_mentions += 1
                if is_valid_temperature(instruction.temperature):
                    valid_temps += 1
            else:
                # Check for temperature mentions in text
                text = instruction.text.lower()
                temps = re.findall(r"(\d+)\s*(?:degrees?|[°℉℃]|f\b|c\b)", text)
                if temps:
                    temp_mentions += len(temps)
                    valid_temps += sum(1 for t in temps if is_valid_temperature(int(t)))

        return valid_temps / temp_mentions if temp_mentions > 0 else 1.0

    def _check_portion_consistency(self, recipe: Recipe) -> float:
        """Check yield/portion consistency."""
        if not recipe.yields:
            return 0.0

        if not is_valid_serving_size(recipe.yields.servings):
            return 0.0

        # Check if ingredient amounts scale reasonably with serving size
        expected_ing_per_serving = 2  # Rough estimate
        actual_ing_per_serving = len(recipe.ingredients) / recipe.yields.servings

        if actual_ing_per_serving < 0.5 * expected_ing_per_serving:
            return 0.5  # Too few ingredients per serving
        if actual_ing_per_serving > 3 * expected_ing_per_serving:
            return 0.5  # Too many ingredients per serving

        return 1.0
