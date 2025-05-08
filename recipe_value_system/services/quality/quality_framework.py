"""
Unified quality framework for recipe value system.

This module provides a consistent approach to quality analysis across
different types of data and use cases in the recipe value system.

Framework for quality assessment of recipes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union

from recipe_value_system.config import SystemConfig


@dataclass
class QualityMetrics:
    """Base class for quality metrics.

    Attributes:
        completeness (float): Completeness score between 0.0 and 1.0.
        consistency (float): Consistency score between 0.0 and 1.0.
        validity (float): Validity score between 0.0 and 1.0.
        overall (float): Overall quality score between 0.0 and 1.0.
    """

    completeness: float = 0.0
    consistency: float = 0.0
    validity: float = 0.0
    overall: float = 0.0


@dataclass
class RecipeQualityMetrics(QualityMetrics):
    """Specific metrics for recipe quality.

    Attributes:
        instruction_clarity (float): Instruction clarity score between 0.0 and 1.0.
        timing_validity (float): Timing validity score between 0.0 and 1.0.
        portion_consistency (float): Portion consistency score between 0.0 and 1.0.
        ingredient_validity (float): Ingredient validity score between 0.0 and 1.0.
    """

    instruction_clarity: float = 0.0
    timing_validity: float = 0.0
    portion_consistency: float = 0.0
    ingredient_validity: float = 0.0


@dataclass
class DataQualityMetrics(QualityMetrics):
    """Specific metrics for data quality.

    Attributes:
        recency (float): Recency score between 0.0 and 1.0.
        volume (float): Volume score between 0.0 and 1.0.
        reliability (float): Reliability score between 0.0 and 1.0.
    """

    recency: float = 0.0
    volume: float = 0.0
    reliability: float = 0.0


class QualityAnalyzer(ABC):
    """Abstract base class for quality analyzers.

    Attributes:
        config (SystemConfig): System configuration.
        min_quality_threshold (float): Minimum quality threshold.
    """

    def __init__(self, config: SystemConfig) -> None:
        """
        Initialize the quality analyzer.

        Args:
            config: System configuration
        """
        self.config = config
        self.min_quality_threshold = 0.6

    @abstractmethod
    def analyze(self, data: Any) -> QualityMetrics:
        """
        Analyze quality of input data.

        Args:
            data: Input data to analyze

        Returns:
            QualityMetrics: Quality metrics for the data
        """
        raise NotImplementedError

    @abstractmethod
    def get_improvement_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """
        Get recommendations for improving quality.

        Args:
            metrics: Quality metrics to base recommendations on

        Returns:
            List[str]: List of improvement recommendations
        """
        raise NotImplementedError

    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate overall quality score from individual metrics.

        Args:
            metrics: Dictionary of metric names to scores

        Returns:
            float: Overall quality score
        """
        if not metrics:
            return 0.0

        # Remove 'overall' from weights calculation
        component_metrics = {k: v for k, v in metrics.items() if k != "overall"}

        if not component_metrics:
            return 0.0

        # Equal weighting for now, could be made configurable
        weights = {metric: 1.0 / len(component_metrics) for metric in component_metrics}

        return sum(
            score * weights[metric] for metric, score in component_metrics.items()
        )


class RecipeQualityAnalyzer(QualityAnalyzer):
    """Analyzer for recipe quality.

    Attributes:
        required_recipe_fields (Set[str]): Set of required recipe fields.
    """

    def __init__(self, config: SystemConfig) -> None:
        """
        Initialize the recipe quality analyzer.

        Args:
            config: System configuration
        """
        super().__init__(config)
        self.required_recipe_fields: Set[str] = {
            "title",
            "ingredients",
            "instructions",
            "yields",
        }

    def analyze(self, recipe: Dict[str, Any]) -> RecipeQualityMetrics:
        """
        Analyze recipe quality across multiple dimensions.

        Args:
            recipe: Recipe data to analyze

        Returns:
            RecipeQualityMetrics: Quality metrics for the recipe
        """
        metrics = RecipeQualityMetrics()

        # Calculate individual scores
        metrics.completeness = self._check_completeness(recipe)
        metrics.instruction_clarity = self._check_instruction_clarity(recipe)
        metrics.ingredient_validity = self._check_ingredient_validity(recipe)
        metrics.timing_validity = self._check_timing_validity(recipe)
        metrics.portion_consistency = self._check_portion_consistency(recipe)
        metrics.consistency = self._check_recipe_consistency(recipe)
        metrics.validity = self._check_recipe_validity(recipe)

        # Calculate overall score
        metrics.overall = self._calculate_overall_score(metrics.__dict__)

        return metrics

    def get_improvement_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """
        Get specific recommendations for improving recipe quality.

        Args:
            metrics: Recipe quality metrics

        Returns:
            List[str]: List of improvement recommendations
        """
        # Cast to the specific metrics type
        recipe_metrics = RecipeQualityMetrics(**metrics.__dict__)
        recommendations = []

        if recipe_metrics.completeness < 0.8:
            recommendations.append(
                "Add missing essential recipe components (ingredients, instructions, yields)"
            )

        if recipe_metrics.instruction_clarity < 0.7:
            recommendations.append(
                "Improve instruction clarity with more detailed steps and precise measurements"
            )

        if recipe_metrics.ingredient_validity < 0.7:
            recommendations.append(
                "Verify ingredient measurements and ensure all ingredients are listed in instructions"
            )

        if recipe_metrics.timing_validity < 0.7:
            recommendations.append(
                "Add specific timing information for each cooking step"
            )

        return recommendations

    def _check_completeness(self, recipe: Dict[str, Any]) -> float:
        """
        Check if recipe has all required components.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Completeness score between 0.0 and 1.0
        """
        if not recipe:
            return 0.0

        present_fields = set(recipe.keys())
        completeness = len(present_fields & self.required_recipe_fields) / len(
            self.required_recipe_fields
        )

        return completeness

    def _check_instruction_clarity(self, recipe: Dict[str, Any]) -> float:
        """
        Check clarity of recipe instructions.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Instruction clarity score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.7

    def _check_ingredient_validity(self, recipe: Dict[str, Any]) -> float:
        """
        Check validity of recipe ingredients.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Ingredient validity score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.8

    def _check_timing_validity(self, recipe: Dict[str, Any]) -> float:
        """
        Check validity of cooking time information.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Timing validity score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.6

    def _check_portion_consistency(self, recipe: Dict[str, Any]) -> float:
        """
        Check consistency of portion information.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Portion consistency score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.7

    def _check_recipe_consistency(self, recipe: Dict[str, Any]) -> float:
        """
        Check overall consistency of recipe.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Recipe consistency score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.75

    def _check_recipe_validity(self, recipe: Dict[str, Any]) -> float:
        """
        Check overall validity of recipe.

        Args:
            recipe: Recipe data to check

        Returns:
            float: Recipe validity score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.8


class DataQualityAnalyzer(QualityAnalyzer):
    """Analyzer for data quality.

    Attributes:
        min_data_points (int): Minimum number of data points.
        max_data_age_days (int): Maximum data age in days.
    """

    def __init__(self, config: SystemConfig) -> None:
        """
        Initialize the data quality analyzer.

        Args:
            config: System configuration
        """
        super().__init__(config)
        self.min_data_points = 5
        self.max_data_age_days = 90

    def analyze(self, data: List[Dict[str, Any]]) -> DataQualityMetrics:
        """
        Analyze data quality across multiple dimensions.

        Args:
            data: List of data items to analyze

        Returns:
            DataQualityMetrics: Quality metrics for the data
        """
        if not data:
            return DataQualityMetrics()

        metrics = DataQualityMetrics()

        # Calculate individual scores
        metrics.completeness = self._check_data_completeness(data)
        metrics.consistency = self._check_data_consistency(data)
        metrics.validity = self._check_data_validity(data)
        metrics.recency = self._check_data_recency(data)
        metrics.volume = self._check_data_volume(data)
        metrics.reliability = self._check_data_reliability(data)

        # Calculate overall score
        metrics.overall = self._calculate_overall_score(metrics.__dict__)

        return metrics

    def get_improvement_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """
        Get specific recommendations for improving data quality.

        Args:
            metrics: Data quality metrics

        Returns:
            List[str]: List of improvement recommendations
        """
        # Cast to the specific metrics type
        data_metrics = DataQualityMetrics(**metrics.__dict__)
        recommendations = []

        if data_metrics.completeness < 0.8:
            recommendations.append("Collect missing data fields")

        if data_metrics.recency < 0.7:
            recommendations.append("Update outdated data points")

        if data_metrics.volume < 0.6:
            recommendations.append("Collect more data points for reliable analysis")

        return recommendations

    def _check_data_completeness(self, data: List[Dict[str, Any]]) -> float:
        """
        Check completeness of data fields.

        Args:
            data: List of data items to check

        Returns:
            float: Completeness score between 0.0 and 1.0
        """
        if not data:
            return 0.0

        required_fields = self._get_required_fields()
        completeness_scores = []

        for item in data:
            present_fields = set(item.keys())
            score = len(present_fields & required_fields) / len(required_fields)
            completeness_scores.append(score)

        return sum(completeness_scores) / len(completeness_scores)

    def _get_required_fields(self) -> Set[str]:
        """
        Get required fields based on data type.

        Returns:
            Set[str]: Set of required field names
        """
        return {
            "id",
            "timestamp",
            "value",
            "source",
        }

    def _check_data_consistency(self, data: List[Dict[str, Any]]) -> float:
        """
        Check consistency of data fields.

        Args:
            data: List of data items to check

        Returns:
            float: Consistency score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.7

    def _check_data_validity(self, data: List[Dict[str, Any]]) -> float:
        """
        Check validity of data fields.

        Args:
            data: List of data items to check

        Returns:
            float: Validity score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.8

    def _check_data_recency(self, data: List[Dict[str, Any]]) -> float:
        """
        Check recency of data.

        Args:
            data: List of data items to check

        Returns:
            float: Recency score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.6

    def _check_data_volume(self, data: List[Dict[str, Any]]) -> float:
        """
        Check volume of data.

        Args:
            data: List of data items to check

        Returns:
            float: Volume score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.75

    def _check_data_reliability(self, data: List[Dict[str, Any]]) -> float:
        """
        Check reliability of data sources.

        Args:
            data: List of data items to check

        Returns:
            float: Reliability score between 0.0 and 1.0
        """
        # Placeholder implementation
        return 0.65


class UnifiedQualityManager:
    """Manager class for coordinating quality analysis.

    Attributes:
        config (SystemConfig): System configuration.
        recipe_analyzer (RecipeQualityAnalyzer): Recipe quality analyzer.
        data_analyzer (DataQualityAnalyzer): Data quality analyzer.
    """

    def __init__(self, config: SystemConfig) -> None:
        """
        Initialize the quality manager.

        Args:
            config: System configuration
        """
        self.config = config
        self.recipe_analyzer = RecipeQualityAnalyzer(config)
        self.data_analyzer = DataQualityAnalyzer(config)

    def analyze_recipe_quality(self, recipe: Dict[str, Any]) -> RecipeQualityMetrics:
        """
        Analyze recipe quality with recommendations.

        Args:
            recipe: Recipe data to analyze

        Returns:
            RecipeQualityMetrics: Quality metrics for the recipe
        """
        metrics = self.recipe_analyzer.analyze(recipe)
        if metrics.overall < self.recipe_analyzer.min_quality_threshold:
            recommendations = self.recipe_analyzer.get_improvement_recommendations(
                metrics
            )
            self._log_quality_issues("recipe", metrics, recommendations)
        return metrics

    def analyze_data_quality(self, data: List[Dict[str, Any]]) -> DataQualityMetrics:
        """
        Analyze data quality with recommendations.

        Args:
            data: List of data items to analyze

        Returns:
            DataQualityMetrics: Quality metrics for the data
        """
        metrics = self.data_analyzer.analyze(data)
        if metrics.overall < self.data_analyzer.min_quality_threshold:
            recommendations = self.data_analyzer.get_improvement_recommendations(
                metrics
            )
            self._log_quality_issues("data", metrics, recommendations)
        return metrics

    def _log_quality_issues(
        self, data_type: str, metrics: QualityMetrics, recommendations: List[str]
    ) -> None:
        """
        Log quality issues and recommendations.

        Args:
            data_type: Type of data being analyzed
            metrics: Quality metrics
            recommendations: List of improvement recommendations
        """
        print(f"Quality issues detected in {data_type}:")
        print(f"Overall quality score: {metrics.overall:.2f}")
        print("Recommendations:")
        for rec in recommendations:
            print(f"- {rec}")
