"""Tests for the learning framework module.

This module tests the basic functionality of the learning framework.
"""

import unittest
from typing import Dict, List

from value.learners import UnifiedLearningManager


class TestLearningFramework(unittest.TestCase):
    """Test cases for the learning framework."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.manager = UnifiedLearningManager()
        self.sample_data = self._create_sample_data()
        self.sample_context = self._create_sample_context()

    def test_initialization(self) -> None:
        """Test that the manager initializes correctly."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(len(self.manager.learners), 4)
        self.assertIn("taste", self.manager.learners)
        self.assertIn("health", self.manager.learners)
        self.assertIn("time", self.manager.learners)
        self.assertIn("effort", self.manager.learners)

    def test_prediction(self) -> None:
        """Test that predictions work correctly."""
        for component in ["taste", "health", "time", "effort"]:
            prediction, confidence = self.manager.predict(
                component, self.sample_data, self.sample_context
            )
            self.assertIsInstance(prediction, float)
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(prediction, 0.0)
            self.assertLessEqual(prediction, 1.0)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)

    def test_feedback(self) -> None:
        """Test that feedback processing works correctly."""
        for component in ["taste", "health", "time", "effort"]:
            # This should not raise any exceptions
            self.manager.process_feedback(
                component, self.sample_data, 0.8, self.sample_context
            )

    def test_feature_importance(self) -> None:
        """Test that feature importance retrieval works correctly."""
        for component in ["taste", "health", "time", "effort"]:
            importance = self.manager.get_feature_importance(component)
            self.assertIsInstance(importance, dict)

    def test_invalid_component(self) -> None:
        """Test that invalid components raise appropriate errors."""
        with self.assertRaises(ValueError):
            self.manager.predict("invalid", self.sample_data)

        with self.assertRaises(ValueError):
            self.manager.process_feedback("invalid", self.sample_data, 0.5)

        with self.assertRaises(ValueError):
            self.manager.get_feature_importance("invalid")

    def _create_sample_data(self) -> Dict[str, List]:
        """Create sample data for testing."""
        return {
            "recipe_id": 123,
            "user_id": 456,
            "ingredients": ["tomato", "basil", "mozzarella"],
            "cuisine": "Italian",
            "preparation_time": 15,
            "cooking_time": 20,
            "difficulty": "medium",
            "nutrition": {
                "calories": 350,
                "protein": 15,
                "carbs": 40,
                "fat": 10,
            },
        }

    def _create_sample_context(self) -> Dict[str, List]:
        """Create sample context for testing."""
        return {
            "time_of_day": "evening",
            "day_of_week": "weekend",
            "season": "summer",
            "occasion": "casual",
        }


if __name__ == "__main__":
    unittest.main()
