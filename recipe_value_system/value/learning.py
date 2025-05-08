"""Learning framework for recipe value calculation.

This module provides the core learning framework for calculating recipe value.
It includes strategies for learning from user feedback and historical data.
"""

from typing import Dict, Optional

import numpy as np
from numpy.typing import NDArray

from recipe_value_system.models.recipe import Recipe
from recipe_value_system.models.user import User


class LearningStrategy(Protocol):
    """Base protocol for learning strategies."""

    def train(self, data: NDArray[np.float64]) -> None:
        """Train the strategy on historical data.

        Args:
            data: Training data array
        """
        ...

    def predict(self, features: NDArray[np.float64]) -> float:
        """Predict value based on features.

        Args:
            features: Input feature array

        Returns:
            Predicted value
        """
        ...


class ValueLearner:
    """Core learning framework for recipe value calculation."""

    def __init__(self, strategies: Dict[str, LearningStrategy]) -> None:
        """Initialize with learning strategies.

        Args:
            strategies: Dict mapping strategy names to implementations
        """
        self.strategies = strategies

    def train(self, data: Dict[str, NDArray[np.float64]]) -> None:
        """Train all learning strategies.

        Args:
            data: Dict mapping strategy names to training data
        """
        for name, strategy in self.strategies.items():
            if name in data:
                strategy.train(data[name])

    def predict(self, features: Dict[str, NDArray[np.float64]]) -> Dict[str, float]:
        """Generate predictions from all strategies.

        Args:
            features: Dict mapping strategy names to feature arrays

        Returns:
            Dict mapping strategy names to predictions
        """
        predictions = {}
        for name, strategy in self.strategies.items():
            if name in features:
                predictions[name] = strategy.predict(features[name])
        return predictions


class ValueCalculator:
    """Calculates overall recipe value using trained strategies."""

    def __init__(self, learner: ValueLearner) -> None:
        """Initialize with value learner.

        Args:
            learner: Trained ValueLearner instance
        """
        self.learner = learner

    def calculate_value(
        self, recipe: Recipe, user: Optional[User] = None
    ) -> Dict[str, float]:
        """Calculate recipe value.

        Args:
            recipe: Recipe to evaluate
            user: Optional user for personalization

        Returns:
            Dict mapping value components to scores
        """
        features = self._extract_features(recipe, user)
        return self.learner.predict(features)

    def _extract_features(
        self, recipe: Recipe, user: Optional[User]
    ) -> Dict[str, NDArray[np.float64]]:
        """Extract features from recipe and user.

        Args:
            recipe: Source recipe
            user: Optional user for personalization

        Returns:
            Dict mapping strategy names to feature arrays
        """
        # Feature extraction implementation
        return {}
