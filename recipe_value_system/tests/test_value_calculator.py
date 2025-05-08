"""
Tests for the value calculator module.

This module contains unit tests for the value calculation functionalities.
"""

import datetime
import json
import os
import sys
import unittest
from typing import Any, Dict, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock modules for testing
import sys
from unittest.mock import MagicMock, patch

# Create mock modules
mock_config = MagicMock()
mock_config.SystemConfig = MagicMock()
sys.modules["config"] = mock_config
sys.modules["config.config"] = mock_config

# Import value components
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


class MockRecipe:
    """Mock recipe for testing.

    Attributes:
        id (int): Unique recipe ID.
        name (str): Recipe name.
        data (Dict[str, Any]): Recipe data.
        nutrition (Dict[str, Any]): Recipe nutrition information.
        ingredients (List[str]): Recipe ingredients.
        preparation_time (int): Recipe preparation time.
        cooking_time (int): Recipe cooking time.
        difficulty (int): Recipe difficulty level.
        cuisine (str): Recipe cuisine.
        meal_type (str): Recipe meal type.
        tags (List[str]): Recipe tags.
    """

    def __init__(self, recipe_id: int, name: str, data: Dict[str, Any]) -> None:
        """Initialize mock recipe."""
        self.id = recipe_id
        self.name = name
        self.data = data
        self.nutrition = data.get("nutrition", {})
        self.ingredients = data.get("ingredients", [])
        self.preparation_time = data.get("preparation_time", 30)
        self.cooking_time = data.get("cooking_time", 45)
        self.difficulty = data.get("difficulty", 3)
        self.cuisine = data.get("cuisine", "Italian")
        self.meal_type = data.get("meal_type", "Dinner")
        self.tags = data.get("tags", [])


class MockUser:
    """Mock user for testing.

    Attributes:
        id (int): Unique user ID.
        name (str): User name.
        data (Dict[str, Any]): User data.
        preferences (Dict[str, Any]): User preferences.
        dietary_restrictions (List[str]): User dietary restrictions.
        skill_level (int): User skill level.
        time_preference (str): User time preference.
        user_type (str): User type.
    """

    def __init__(self, user_id: int, name: str, data: Dict[str, Any]) -> None:
        """Initialize mock user."""
        self.id = user_id
        self.name = name
        self.data = data
        self.preferences = data.get("preferences", {})
        self.dietary_restrictions = data.get("dietary_restrictions", [])
        self.skill_level = data.get("skill_level", 3)
        self.time_preference = data.get("time_preference", "medium")
        self.user_type = data.get("user_type", "regular")


class MockSession:
    """Mock database session for testing.

    Attributes:
        recipes (Dict[int, MockRecipe]): Mock recipes.
        users (Dict[int, MockUser]): Mock users.
    """

    def __init__(self, recipes: List[MockRecipe], users: List[MockUser]) -> None:
        """Initialize mock session with test data."""
        self.recipes = {recipe.id: recipe for recipe in recipes}
        self.users = {user.id: user for user in users}

    def query(self, model_class: Any) -> "MockQuery":
        """Mock query method."""
        return MockQuery(self)

    def add(self, obj: Any) -> None:
        """Mock add method."""
        pass

    def commit(self) -> None:
        """Mock commit method."""
        pass


class MockQuery:
    """Mock query result for testing.

    Attributes:
        session (MockSession): Mock session.
        filters (Dict[str, Any]): Query filters.
    """

    def __init__(self, session: MockSession) -> None:
        """Initialize mock query."""
        self.session = session
        self.filters = {}

    def filter_by(self, **kwargs: Any) -> "MockQuery":
        """Mock filter_by method."""
        self.filters.update(kwargs)
        return self

    def first(self) -> Optional[Any]:
        """Mock first method."""
        if "id" in self.filters:
            recipe_id = self.filters.get("id")
            if recipe_id in self.session.recipes:
                return self.session.recipes[recipe_id]
            elif recipe_id in self.session.users:
                return self.session.users[recipe_id]
        return None

    def all(self) -> List[Any]:
        """Mock all method."""
        return list(self.session.recipes.values())


class MockSystemConfig:
    """Mock system configuration for testing.

    Attributes:
        value (Dict[str, Any]): Value configuration.
        database (Dict[str, Any]): Database configuration.
        logging (Dict[str, Any]): Logging configuration.
    """

    def __init__(self) -> None:
        """Initialize mock config."""
        self.value = {
            "default_mode": "standard",
            "confidence_threshold": 0.6,
            "cache_ttl_hours": 1,
        }
        self.database = {"url": "mock://localhost/test"}
        self.logging = {"level": "INFO"}

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if section in self.__dict__ and key in self.__dict__[section]:
            return self.__dict__[section][key]
        return default


class TestValueCalculator(unittest.TestCase):
    """Test the value calculator functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Load test data
        self.test_recipes = [
            MockRecipe(
                1,
                "Spaghetti Carbonara",
                {
                    "nutrition": {
                        "calories": 650,
                        "protein": 25,
                        "fat": 30,
                        "carbs": 70,
                    },
                    "ingredients": ["pasta", "eggs", "bacon", "cheese", "pepper"],
                    "preparation_time": 15,
                    "cooking_time": 20,
                    "difficulty": 2,
                    "cuisine": "Italian",
                    "meal_type": "Dinner",
                    "tags": ["pasta", "quick", "comfort food"],
                },
            ),
            MockRecipe(
                2,
                "Grilled Chicken Salad",
                {
                    "nutrition": {
                        "calories": 350,
                        "protein": 35,
                        "fat": 15,
                        "carbs": 20,
                    },
                    "ingredients": [
                        "chicken",
                        "lettuce",
                        "tomato",
                        "cucumber",
                        "olive oil",
                    ],
                    "preparation_time": 20,
                    "cooking_time": 15,
                    "difficulty": 1,
                    "cuisine": "American",
                    "meal_type": "Lunch",
                    "tags": ["healthy", "protein", "low-carb"],
                },
            ),
        ]

        self.test_users = [
            MockUser(
                1,
                "Regular User",
                {
                    "preferences": {
                        "cuisines": ["Italian", "Mexican"],
                        "ingredients": ["pasta", "cheese", "chicken"],
                        "meal_types": ["Dinner", "Lunch"],
                    },
                    "dietary_restrictions": [],
                    "skill_level": 3,
                    "time_preference": "medium",
                    "user_type": "regular",
                },
            ),
            MockUser(
                2,
                "Premium User",
                {
                    "preferences": {
                        "cuisines": ["Asian", "Mediterranean"],
                        "ingredients": ["fish", "rice", "vegetables"],
                        "meal_types": ["Dinner", "Breakfast"],
                    },
                    "dietary_restrictions": ["gluten"],
                    "skill_level": 4,
                    "time_preference": "short",
                    "user_type": "premium",
                },
            ),
        ]

        # Set up mock session and config
        self.session = MockSession(self.test_recipes, self.test_users)
        self.config = MockSystemConfig()

        # Initialize components for testing
        self.health_calculator = HealthCalculator(self.session, self.config)
        self.taste_calculator = TasteCalculator(self.session, self.config)
        self.confidence_calculator = ConfidenceCalculator(self.config)
        self.context_manager = ContextManager(self.session)
        self.feedback_learner = FeedbackLearner(self.session, self.config)
        self.quality_monitor = DataQualityMonitor(self.session)

        # Initialize the unified calculator
        self.calculator = UnifiedValueCalculator(self.session, self.config)

        # Set calculator to testing mode to avoid external dependencies
        self.calculator._testing_mode = True

    def test_health_calculator(self) -> None:
        """Test the health calculator component."""
        recipe = self.test_recipes[0]  # Spaghetti Carbonara
        user = self.test_users[0]  # Regular User

        # Mock the necessary methods
        with patch.object(
            self.health_calculator,
            "_get_recipe_nutrition",
            return_value=recipe.nutrition,
        ):
            with patch.object(
                self.health_calculator, "_get_user_health_goals", return_value={}
            ):
                # Calculate health score
                health_score = self.health_calculator.calculate(recipe.id, user.id)

                # Assert that the health score is within the expected range
                self.assertIsInstance(health_score, float)
                self.assertGreaterEqual(health_score, 0.0)
                self.assertLessEqual(health_score, 1.0)

    def test_taste_calculator(self) -> None:
        """Test the taste calculator component."""
        recipe = self.test_recipes[0]  # Spaghetti Carbonara
        user = self.test_users[0]  # Regular User

        # Mock the necessary methods
        with patch.object(
            self.taste_calculator, "_get_recipe_profile", return_value={}
        ):
            with patch.object(
                self.taste_calculator,
                "_get_user_preferences",
                return_value=user.preferences,
            ):
                # Calculate taste score
                taste_score = self.taste_calculator.calculate(recipe.id, user.id)

                # Assert that the taste score is within the expected range
                self.assertIsInstance(taste_score, float)
                self.assertGreaterEqual(taste_score, 0.0)
                self.assertLessEqual(taste_score, 1.0)

    def test_confidence_calculator(self) -> None:
        """Test the confidence calculator component."""
        # Create test data
        components = {
            "taste": 0.8,
            "health": 0.7,
            "time": 0.6,
            "effort": 0.5,
            "cost": 0.4,
        }

        # Calculate confidence scores
        confidence_scores = self.confidence_calculator.calculate(components)

        # Assert that confidence scores are returned for each component
        self.assertIsInstance(confidence_scores, dict)
        for component in components:
            self.assertIn(component, confidence_scores)
            self.assertIsInstance(confidence_scores[component], float)
            self.assertGreaterEqual(confidence_scores[component], 0.0)
            self.assertLessEqual(confidence_scores[component], 1.0)

    def test_context_manager(self) -> None:
        """Test the context manager component."""
        user_id = 1

        # Mock the necessary methods
        with patch.object(self.context_manager, "_get_user_data", return_value={}):
            with patch.object(
                self.context_manager, "_get_time_context", return_value={}
            ):
                # Build context
                context = self.context_manager.build_context(user_id)

                # Assert that context is returned with expected keys
                self.assertIsInstance(context, dict)
                self.assertIn("timestamp", context)
                self.assertIsInstance(context["timestamp"], datetime.datetime)

    def test_unified_calculator_simple_mode(self) -> None:
        """Test the unified calculator in simple mode."""
        recipe_id = 1
        user_id = 1

        # Calculate value in simple mode
        result = self.calculator.calculate_value(recipe_id, user_id, ValueMode.SIMPLE)

        # Assert that the result has the expected structure
        self.assertIsInstance(result, ValueResult)
        self.assertEqual(result.recipe_id, recipe_id)
        self.assertEqual(result.user_id, user_id)
        self.assertIsInstance(result.overall, float)
        self.assertGreaterEqual(result.overall, 0.0)
        self.assertLessEqual(result.overall, 1.0)

        # Check components
        self.assertIsInstance(result.components, ValueComponents)
        self.assertGreaterEqual(result.components.taste, 0.0)
        self.assertLessEqual(result.components.taste, 1.0)

    def test_unified_calculator_standard_mode(self) -> None:
        """Test the unified calculator in standard mode."""
        recipe_id = 1
        user_id = 1

        # Calculate value in standard mode
        result = self.calculator.calculate_value(recipe_id, user_id, ValueMode.STANDARD)

        # Assert that the result has the expected structure
        self.assertIsInstance(result, ValueResult)
        self.assertEqual(result.recipe_id, recipe_id)
        self.assertEqual(result.user_id, user_id)
        self.assertIsInstance(result.overall, float)
        self.assertGreaterEqual(result.overall, 0.0)

        # Check components
        self.assertIsInstance(result.components, ValueComponents)
        self.assertGreaterEqual(result.components.taste, 0.0)
        self.assertLessEqual(result.components.taste, 1.0)
        self.assertGreaterEqual(result.components.health, 0.0)
        self.assertLessEqual(result.components.health, 1.0)
        self.assertGreaterEqual(result.components.time, 0.0)
        self.assertLessEqual(result.components.time, 1.0)
        self.assertGreaterEqual(result.components.effort, 0.0)
        self.assertLessEqual(result.components.effort, 1.0)
        self.assertGreaterEqual(result.components.cost, 0.0)
        self.assertLessEqual(result.components.cost, 1.0)

    def test_unified_calculator_with_confidence(self) -> None:
        """Test the unified calculator with confidence scoring."""
        recipe_id = 1
        user_id = 1

        # Calculate value with confidence
        result = self.calculator.calculate_value(
            recipe_id, user_id, ValueMode.STANDARD, with_confidence=True
        )

        # Assert that confidence scores are included
        self.assertIsNotNone(result.confidence)
        self.assertIsInstance(result.confidence, dict)

        # Check that confidence scores are provided for each component
        for component in ["taste", "health", "time", "effort", "cost"]:
            self.assertIn(component, result.confidence)
            self.assertIsInstance(result.confidence[component], float)
            self.assertGreaterEqual(result.confidence[component], 0.0)
            self.assertLessEqual(result.confidence[component], 1.0)

    def test_unified_calculator_with_context(self) -> None:
        """Test the unified calculator with context information."""
        recipe_id = 1
        user_id = 1

        # Create test context
        context = {
            "time_of_day": "evening",
            "day_of_week": "weekend",
            "season": "summer",
            "user_mood": "hungry",
        }

        # Calculate value with context
        result = self.calculator.calculate_value(
            recipe_id, user_id, ValueMode.STANDARD, context=context
        )

        # Assert that the result has the expected structure
        self.assertIsInstance(result, ValueResult)
        self.assertEqual(result.recipe_id, recipe_id)
        self.assertEqual(result.user_id, user_id)
        self.assertIsInstance(result.overall, float)

        # Context should influence the result, but we can't test the exact values
        # Just ensure we get a valid result
        self.assertGreaterEqual(result.overall, 0.0)

    def test_feedback_learner(self) -> None:
        """Test the feedback learner component."""
        user_id = 1
        recipe_id = 1
        feedback = {
            "rating": 4.5,
            "components": {
                "taste": 0.9,
                "health": 0.7,
                "time": 0.6,
                "effort": 0.5,
                "cost": 0.8,
            },
            "context": {"time_of_day": "evening", "day_of_week": "weekend"},
        }

        # Process feedback
        with patch.object(self.feedback_learner, "_store_feedback", return_value=None):
            with patch.object(
                self.feedback_learner, "_update_user_preferences", return_value=None
            ):
                # Just test that the method doesn't raise an exception
                self.feedback_learner.submit_feedback(user_id, recipe_id, feedback)

        # Get updated preferences
        with patch.object(
            self.feedback_learner, "_get_user_preferences", return_value={}
        ):
            preferences = self.feedback_learner.get_user_preferences(user_id)

            # Assert that preferences are returned
            self.assertIsInstance(preferences, dict)

    def test_quality_monitor(self) -> None:
        """Test the data quality monitor component."""
        recipe_id = 1

        # Check recipe data quality
        with patch.object(
            self.quality_monitor, "_get_recipe", return_value=self.test_recipes[0]
        ):
            quality_score = self.quality_monitor.check_quality(recipe_id)

            # Assert that quality score is within the expected range
            self.assertIsInstance(quality_score, float)
            self.assertGreaterEqual(quality_score, 0.0)
            self.assertLessEqual(quality_score, 1.0)


if __name__ == "__main__":
    unittest.main()
