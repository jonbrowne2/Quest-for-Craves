"""
Tests for the value types module.

This module contains unit tests for various value types used in the application.
"""

import os
import sys
import unittest
from typing import Any, Dict, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Mock SystemConfig for testing
class MockSystemConfig:
    """
    Mock system configuration for testing.

    This class provides a mock implementation of the SystemConfig class for testing purposes.
    """

    def __init__(self) -> None:
        """Initialize mock config."""
        self.value = {"default_mode": "standard"}

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            section (str): Configuration section.
            key (str): Configuration key.
            default (Any, optional): Default value. Defaults to None.

        Returns:
            Any: Configuration value.
        """
        if section == "value" and key in self.value:
            return self.value[key]
        return default


# Mock the config module
import sys
from unittest.mock import MagicMock

# Create mock modules
mock_config = MagicMock()
mock_config.SystemConfig = MockSystemConfig
sys.modules["config"] = mock_config
sys.modules["config.config"] = mock_config

# Now import the value modules
from value import (
    ConfidenceCalculator,
    ContextManager,
    DataQualityMonitor,
    FeedbackLearner,
    UnifiedValueCalculator,
    ValueComponents,
    ValueMode,
    ValueResult,
)
from value.components.health_calculator import HealthCalculator
from value.components.taste_calculator import TasteCalculator


class MockSession:
    """
    Mock database session for testing.

    This class provides a mock implementation of the database session for testing purposes.
    """

    def query(self, *args: Any, **kwargs: Any) -> "MockQuery":
        """Mock query method."""
        return MockQuery()

    def add(self, obj: Any) -> None:
        """Mock add method."""
        pass

    def commit(self) -> None:
        """Mock commit method."""
        pass


class MockQuery:
    """
    Mock query result for testing.

    This class provides a mock implementation of the query result for testing purposes.
    """

    def filter_by(self, *args: Any, **kwargs: Any) -> "MockQuery":
        """Mock filter_by method."""
        return self

    def first(self) -> Optional[Dict[str, Any]]:
        """Mock first method."""
        return {"id": 1, "name": "Test Recipe"}

    def all(self) -> list:
        """Mock all method."""
        return [{"id": 1, "name": "Test Recipe"}]


class TestValueTypeAnnotations(unittest.TestCase):
    """
    Test type annotations in value module.

    This class contains unit tests for type annotations in the value module.
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.config = MockSystemConfig()
        self.session = MockSession()

    def test_value_components_type_safety(self) -> None:
        """Test that ValueComponents can be created with proper types."""
        components = ValueComponents(
            taste=0.8, health=0.7, time=0.6, effort=0.5, cost=0.4, overall=0.7
        )
        self.assertEqual(components.taste, 0.8)
        self.assertEqual(components.health, 0.7)
        self.assertEqual(components.time, 0.6)
        self.assertEqual(components.effort, 0.5)
        self.assertEqual(components.cost, 0.4)
        self.assertEqual(components.overall, 0.7)

    def test_value_result_type_safety(self) -> None:
        """Test that ValueResult can be created with proper types."""
        components = ValueComponents(
            taste=0.8, health=0.7, time=0.6, effort=0.5, cost=0.4, overall=0.7
        )

        result = ValueResult(
            recipe_id=1,
            user_id=2,
            overall=0.75,
            components=components,
            confidence={"taste": 0.9, "health": 0.8},
            reliability={"data_quality": 0.85},
            explanation={"taste": "Good flavor profile"},
        )

        self.assertEqual(result.recipe_id, 1)
        self.assertEqual(result.user_id, 2)
        self.assertEqual(result.overall, 0.75)
        self.assertEqual(result.components.taste, 0.8)
        self.assertEqual(result.confidence.get("taste"), 0.9)
        self.assertEqual(result.reliability.get("data_quality"), 0.85)
        self.assertEqual(result.explanation.get("taste"), "Good flavor profile")

    def test_calculator_imports(self) -> None:
        """Test that calculator classes can be imported and instantiated."""
        health_calc = HealthCalculator()
        taste_calc = TasteCalculator()

        self.assertIsInstance(health_calc, HealthCalculator)
        self.assertIsInstance(taste_calc, TasteCalculator)

    def test_value_mode_enum(self) -> None:
        """Test that ValueMode enum works correctly."""
        self.assertEqual(ValueMode.SIMPLE.value, "simple")
        self.assertEqual(ValueMode.STANDARD.value, "standard")
        self.assertEqual(ValueMode.COMPLEX.value, "complex")
        self.assertEqual(ValueMode.PERSONALIZED.value, "personalized")

    def test_support_modules(self) -> None:
        """Test that support modules can be imported and instantiated."""
        confidence_calc = ConfidenceCalculator()
        context_manager = ContextManager(self.session)
        feedback_learner = FeedbackLearner(self.session)
        quality_monitor = DataQualityMonitor(self.session)

        self.assertIsInstance(confidence_calc, ConfidenceCalculator)
        self.assertIsInstance(context_manager, ContextManager)
        self.assertIsInstance(feedback_learner, FeedbackLearner)
        self.assertIsInstance(quality_monitor, DataQualityMonitor)

    def test_unified_calculator(self) -> None:
        """Test that UnifiedValueCalculator can be instantiated."""
        calculator = UnifiedValueCalculator(self.session, self.config)

        self.assertIsInstance(calculator, UnifiedValueCalculator)


if __name__ == "__main__":
    unittest.main()
