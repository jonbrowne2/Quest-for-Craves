"""Environment-specific configuration module for the Recipe Value System."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class EnvironmentConfig(BaseModel):
    """Environment-specific configuration settings."""

    name: str = Field(default="development", description="Environment name")
    database_url: str = Field(
        default="sqlite:///vault/recipes.db", description="Database URL"
    )
    debug_mode: bool = Field(default=False, description="Enable debug mode")


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary to merge on top

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_environment_config(env_name: Optional[str] = None) -> Dict[str, Any]:
    """Load environment-specific configuration.

    Args:
        env_name: Target environment name

    Returns:
        Dictionary of environment-specific settings
    """
    if not env_name:
        env_name = os.getenv("RECIPE_VALUE_ENV", "development")

    base_config: Dict[str, Any] = {
        "system": {
            "name": "Recipe Value System",
            "version": "1.0.0",
            "debug": False,
            "log_level": "INFO",
        },
        "database": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "name": "recipe_value",
            "user": "postgres",
            "password": "",
            "pool_size": 5,
            "max_overflow": 10,
            "timeout": 30,
        },
        "cache": {
            "type": "redis",
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None,
            "ttl": 3600,  # 1 hour in seconds
        },
        "value": {
            "default_mode": "standard",
            "confidence_threshold": 0.6,
            "cache_ttl_hours": 1,
            "component_weights": {
                "taste": 0.35,
                "health": 0.25,
                "time": 0.15,
                "effort": 0.15,
                "cost": 0.10,
            },
        },
        "api": {
            "host": "0.0.0.0",
            "port": 5000,
            "workers": 4,
            "timeout": 60,
            "rate_limit": 100,  # requests per minute
        },
    }

    config_map: Dict[str, Dict[str, Any]] = {
        "development": {
            "system": {
                "debug": True,
                "log_level": "DEBUG",
            },
            "database": {
                "name": "recipe_value_dev",
            },
            "cache": {
                "ttl": 300,  # 5 minutes in seconds
            },
            "value": {
                "cache_ttl_hours": 0.5,  # 30 minutes
            },
            "api": {
                "workers": 1,
                "rate_limit": 0,  # no rate limit in development
            },
        },
        "staging": {
            "system": {
                "debug": True,
                "log_level": "INFO",
            },
            "database": {
                "name": "recipe_value_staging",
            },
            "cache": {
                "type": "memory",
                "ttl": 60,  # 1 minute in seconds
            },
            "value": {
                "cache_ttl_hours": 0.1,  # 6 minutes
            },
            "api": {
                "workers": 1,
                "rate_limit": 0,  # no rate limit in staging
            },
        },
        "production": {
            "system": {
                "debug": False,
                "log_level": "WARNING",
            },
            "database": {
                "pool_size": 10,
                "max_overflow": 20,
            },
            "cache": {
                "ttl": 7200,  # 2 hours in seconds
            },
            "value": {
                "cache_ttl_hours": 2,  # 2 hours
            },
            "api": {
                "workers": 8,
                "timeout": 30,
            },
        },
    }

    if env_name not in config_map:
        return {}

    config = deep_merge(base_config, config_map[env_name])

    # Load from config file if it exists
    config_path = os.environ.get("RECIPE_VALUE_CONFIG")
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config = deep_merge(config, file_config)
        except (yaml.YAMLError, OSError) as e:
            print(f"Error loading config file: {e}")

    return config


def get_database_url(config: Dict[str, Any]) -> str:
    """Get database URL from configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Database URL string
    """
    if "database_url" in config:
        return config["database_url"]

    return "sqlite:///vault/recipes.db"
