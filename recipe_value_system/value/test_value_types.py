"""Test cases for value types and caching in the Recipe Value System."""

import unittest
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel

from ..config.config import SystemConfig
from ..value.calculator import (
    ComponentLearner,
    EffortLearner,
    HealthLearner,
    TasteLearner,
    TimeLearner,
    ValueCache,
)


class ValueMode(Enum):
    """Value calculation modes."""

    SIMPLE = "simple"
    STANDARD = "standard"
    PERSONALIZED = "personalized"


class MockSystemConfig(BaseModel):
    """Mock system configuration for testing."""

    app_name: str = "Recipe Value System Test"
    version: str = "0.1.0"
    env: str = "test"
    value_config: Dict[str, float] = {
        "taste_weight": 0.4,
        "texture_weight": 0.2,
        "nutrition_weight": 0.2,
        "cost_weight": 0.2,
    }


@dataclass
class ValueComponents:
    """Mock value components for testing."""

    taste: float = 0.0
    health: float = 0.0
    time: float = 0.0
    effort: float = 0.0
    cost: float = 0.0
    overall: float = 0.0


@dataclass
class ValueResult:
    """Mock value result for testing."""

    recipe_id: int
    user_id: int
    overall: float
    components: ValueComponents


class ModelProtocol:
    """Protocol defining the interface for ML models."""

    def fit(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> None:
        """Fit the model to training data.

        Args:
            X: Feature matrix.
            y: Target values.
        """
        ...

    def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Make predictions using the model.

        Args:
            X: Feature matrix.

        Returns:
            Array of predictions.
        """
        ...


class ScalerProtocol:
    """Protocol defining the interface for feature scalers."""

    def fit_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Fit the scaler and transform the data.

        Args:
            X: Input data.

        Returns:
            Scaled data.
        """
        ...

    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Transform data using the fitted scaler.

        Args:
            X: Input data.

        Returns:
            Scaled data.
        """
        ...


class MockModel:
    """Mock model for testing ML components."""

    def fit(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> None:
        """Mock fit method that does nothing.

        Args:
            X: Feature matrix.
            y: Target values.
        """
        pass

    def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Mock predict method that returns constant predictions.

        Args:
            X: Feature matrix.

        Returns:
            Array of constant predictions (0.5).
        """
        return np.array([0.5], dtype=np.float64)


class MockScaler:
    """Mock scaler for testing feature scaling."""

    def fit_transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Mock fit_transform method that returns input unchanged.

        Args:
            X: Input data.

        Returns:
            Input data unchanged.
        """
        return X

    def transform(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """Mock transform method that returns input unchanged.

        Args:
            X: Input data.

        Returns:
            Input data unchanged.
        """
        return X


class MockConfig(SystemConfig):
    """Mock configuration for testing value components."""

    def __init__(self, value_config: Optional[Dict[str, float]] = None) -> None:
        """Initialize mock config.

        Args:
            value_config: Optional value calculation configuration
        """
        super().__init__()
        self.value = value_config or {}

    def get_value_config(self) -> Dict[str, float]:
        """Get mock value configuration.

        Returns:
            Dictionary containing mock value weights.
        """
        return self.value


class MockSession:
    """Mock database session for testing."""

    def query(self, *args: Any, **kwargs: Any) -> "MockSession":
        """Mock query method that returns self.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Self for method chaining.
        """
        return self

    def filter(self, *args: Any, **kwargs: Any) -> "MockSession":
        """Mock filter method that returns self.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Self for method chaining.
        """
        return self

    def all(self) -> List[Any]:
        """Mock all method that returns empty list.

        Returns:
            Empty list.
        """
        return []

    def first(self) -> None:
        """Mock first method that returns None.

        Returns:
            None.
        """
        return None


@unittest.skipIf(
    ComponentLearner is None, "Skipping ComponentLearner tests due to missing imports"
)
class TestComponentLearner(unittest.TestCase):
    """Test cases for ComponentLearner and derived classes."""

    def setUp(self) -> None:
        """Set up test fixtures.

        Creates mock instances of all learner components with appropriate
        configuration and session objects.
        """
        self.config = MockConfig()
        self.session = MockSession()

        # Create learners with mocked numpy random
        with patch("numpy.random.rand") as mock_rand:
            mock_rand.return_value = np.array([0.5] * 10, dtype=np.float64)
            self.taste_learner = TasteLearner(config=self.config, session=self.session)
            self.health_learner = HealthLearner(
                config=self.config, session=self.session
            )
            self.time_learner = TimeLearner(config=self.config, session=self.session)
            self.effort_learner = EffortLearner(
                config=self.config, session=self.session
            )

        # Replace models and scalers with mocks
        for learner in [
            self.taste_learner,
            self.health_learner,
            self.time_learner,
            self.effort_learner,
        ]:
            learner.model = MockModel()
            learner.scaler = MockScaler()

    def test_feature_extraction(self) -> None:
        """Test feature extraction with proper types.

        Verifies that feature extraction works correctly for all learner
        components and produces properly typed numpy arrays.
        """
        recipe_data = {
            "ingredients": ["salt", "pepper"],
            "cuisine": "italian",
            "cooking_time": 30,
            "preparation_time": 15,
            "difficulty": "medium",
        }

        user_data = {
            "liked_ingredients": ["salt"],
            "disliked_ingredients": ["pepper"],
            "preferred_cuisines": ["italian"],
            "available_time": 60,
        }

        # Test taste features
        taste_features = self.taste_learner.extract_features(recipe_data, user_data)
        self.assertIsInstance(taste_features, np.ndarray)
        self.assertEqual(taste_features.dtype, np.float64)
        self.assertEqual(len(taste_features), len(self.taste_learner.feature_names))

        # Test health features
        health_features = self.health_learner.extract_features(recipe_data, user_data)
        self.assertIsInstance(health_features, np.ndarray)
        self.assertEqual(health_features.dtype, np.float64)
        self.assertEqual(len(health_features), len(self.health_learner.feature_names))

        # Test time features
        time_features = self.time_learner.extract_features(recipe_data, user_data)
        self.assertIsInstance(time_features, np.ndarray)
        self.assertEqual(time_features.dtype, np.float64)
        self.assertEqual(len(time_features), len(self.time_learner.feature_names))

        # Test effort features
        effort_features = self.effort_learner.extract_features(recipe_data, user_data)
        self.assertIsInstance(effort_features, np.ndarray)
        self.assertEqual(effort_features.dtype, np.float64)
        self.assertEqual(len(effort_features), len(self.effort_learner.feature_names))

    def test_model_update(self) -> None:
        """Test model update with proper types.

        Verifies that model updates work correctly and maintain proper typing
        of training data and history.
        """
        features = np.array([0.5] * 10, dtype=np.float64)
        value = 0.8

        # Test update
        self.taste_learner.update(features, value)
        self.assertGreater(len(self.taste_learner.training_history), 0)
        self.assertIsNotNone(self.taste_learner.last_training_time)

    @patch("numpy.random.rand")
    def test_model_prediction(self, mock_rand: MagicMock) -> None:
        """Test model prediction with proper types.

        Args:
            mock_rand: Mocked numpy random function.

        Verifies that model predictions work correctly and maintain proper
        typing of input features and output predictions.
        """
        # Mock numpy random for consistent testing
        mock_rand.return_value = np.array([0.5], dtype=np.float64)

        # Create test data
        features = np.array([0.5] * 10, dtype=np.float64)

        # Test prediction
        prediction = self.taste_learner.predict(features)
        self.assertIsInstance(prediction, float)
        self.assertGreaterEqual(prediction, 0.0)
        self.assertLessEqual(prediction, 1.0)


class TestValueCache(unittest.TestCase):
    """Test cases for ValueCache system."""

    def setUp(self) -> None:
        """Set up test fixtures.

        Creates a fresh cache instance and test data for each test.
        """
        self.cache = ValueCache()
        self.test_key = "test_recipe_1"
        self.test_result = ValueResult(
            recipe_id=1,
            user_id=1,
            overall=0.8,
            components=ValueComponents(
                taste=0.9,
                health=0.8,
                time=0.7,
                effort=0.6,
                cost=0.5,
                overall=0.8,
            ),
        )
        self.test_context = {"user_id": 1, "preferences": {"taste": 0.8}}

    def test_cache_operations(self) -> None:
        """Test basic cache operations.

        Verifies that cache set and get operations work correctly and
        maintain proper typing of stored results.
        """
        # Test cache miss
        self.assertIsNone(self.cache.get(self.test_key))

        # Test cache hit
        self.cache.set(self.test_key, self.test_result, self.test_context)
        cached_result = self.cache.get(self.test_key, self.test_context)
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result.overall, self.test_result.overall)

    def test_cache_eviction(self) -> None:
        """Test cache eviction.

        Verifies that cache eviction works correctly when the cache is full
        or entries are expired.
        """
        # Fill cache to capacity
        for i in range(1000):
            key = f"test_recipe_{i}"
            result = ValueResult(
                recipe_id=i,
                user_id=1,
                overall=0.8,
                components=ValueComponents(),
            )
            self.cache.set(key, result)

        # Verify cache size is maintained
        self.assertLessEqual(len(self.cache._cache), self.cache.max_size)

    def test_context_matching(self) -> None:
        """Test context-based cache matching.

        Verifies that cache entries are properly matched based on their
        associated context.
        """
        # Test with matching context
        self.cache.set(self.test_key, self.test_result, self.test_context)
        self.assertIsNotNone(self.cache.get(self.test_key, self.test_context))

        # Test with non-matching context
        different_context = {"user_id": 2, "preferences": {"taste": 0.5}}
        self.assertIsNone(self.cache.get(self.test_key, different_context))

    def test_cache_statistics(self) -> None:
        """Test cache statistics tracking.

        Verifies that cache hit/miss statistics are properly tracked and
        updated.
        """
        # Test initial stats
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)

        # Test stats after operations
        self.cache.get(self.test_key)  # Miss
        self.assertEqual(self.cache.misses, 1)

        self.cache.set(self.test_key, self.test_result)
        self.cache.get(self.test_key)  # Hit
        self.assertEqual(self.cache.hits, 1)


if __name__ == "__main__":
    unittest.main()
