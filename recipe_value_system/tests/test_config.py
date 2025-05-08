"""
Tests for the configuration module.

This module contains unit tests for the configuration settings.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import SystemConfig
from config.environments import get_database_url, load_environment_config


class TestEnvironmentConfig(unittest.TestCase):
    """
    Test the environment-based configuration system.
    """

    def test_load_dev_config(self):
        """
        Test loading development configuration.
        """
        config = load_environment_config("dev")

        # Check that the config has the expected sections
        self.assertIn("system", config)
        self.assertIn("database", config)
        self.assertIn("cache", config)
        self.assertIn("value", config)
        self.assertIn("api", config)

        # Check some specific values
        self.assertTrue(config["system"]["debug"])
        self.assertEqual(config["system"]["log_level"], "DEBUG")
        self.assertEqual(config["database"]["name"], "recipe_value_dev")

    def test_load_test_config(self):
        """
        Test loading test configuration.
        """
        config = load_environment_config("test")

        # Check that the config has the expected sections
        self.assertIn("system", config)
        self.assertIn("database", config)
        self.assertIn("cache", config)
        self.assertIn("value", config)
        self.assertIn("api", config)

        # Check some specific values
        self.assertTrue(config["system"]["debug"])
        self.assertEqual(config["system"]["log_level"], "DEBUG")
        self.assertEqual(config["database"]["name"], "recipe_value_test")
        self.assertEqual(config["cache"]["type"], "memory")

    def test_load_prod_config(self):
        """
        Test loading production configuration.
        """
        config = load_environment_config("prod")

        # Check that the config has the expected sections
        self.assertIn("system", config)
        self.assertIn("database", config)
        self.assertIn("cache", config)
        self.assertIn("value", config)
        self.assertIn("api", config)

        # Check some specific values
        self.assertFalse(config["system"]["debug"])
        self.assertEqual(config["system"]["log_level"], "WARNING")
        self.assertEqual(config["database"]["pool_size"], 10)

    def test_get_database_url(self):
        """
        Test generating database URL from configuration.
        """
        config = load_environment_config("dev")
        url = get_database_url(config)

        # Check that the URL has the expected format
        self.assertTrue(url.startswith("postgresql://"))
        self.assertIn("recipe_value_dev", url)


class TestSystemConfig(unittest.TestCase):
    """
    Test the SystemConfig class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        # Save original environment variables
        self.original_env = os.environ.copy()

    def tearDown(self):
        """
        Tear down test fixtures.
        """
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_config(self):
        """
        Test creating SystemConfig with default settings.
        """
        config = SystemConfig()

        # Check that the config has the expected attributes
        self.assertEqual(config.app_name, "Recipe Value System")
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.env, "development")

        # Check database settings
        self.assertTrue(hasattr(config, "database"))
        self.assertTrue(hasattr(config.database, "url"))

        # Check Redis settings
        self.assertTrue(hasattr(config, "redis"))
        self.assertEqual(config.redis.host, "localhost")
        self.assertEqual(config.redis.port, 6379)

    def test_env_var_config(self):
        """
        Test creating SystemConfig with environment variables.
        """
        # Set environment variables
        os.environ["RECIPE_VALUE_ENV"] = "dev"

        config = SystemConfig()

        # Check that the environment was set correctly
        self.assertEqual(config.env, "dev")

        # Check that environment-specific settings were applied
        self.assertTrue(config.get_environment_settings()["debug"])

    def test_get_method(self):
        """
        Test the get method of SystemConfig.
        """
        config = SystemConfig()

        # Set environment config manually for testing
        config.env_config = {
            "system": {"name": "Recipe Value System", "version": "2.0.0"},
            "value": {
                "default_mode": "advanced",
                "component_weights": {"taste": 0.4, "health": 0.3},
            },
        }

        # Test getting values from environment config
        self.assertEqual(config.get("system", "name"), "Recipe Value System")
        self.assertEqual(config.get("value", "default_mode"), "advanced")
        self.assertEqual(config.get("value", "component_weights")["taste"], 0.4)

        # Test getting values from attributes
        self.assertEqual(config.get("database", "url"), config.database.url)

        # Test getting non-existent values
        self.assertIsNone(config.get("nonexistent", "key"))
        self.assertEqual(config.get("nonexistent", "key", "default"), "default")


if __name__ == "__main__":
    unittest.main()
