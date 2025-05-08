"""Type-safe configuration management."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set

import yaml
from pydantic import BaseSettings, PostgresDsn, RedisDsn


@dataclass
class DatabaseConfig:
    """Database configuration with type safety."""

    url: PostgresDsn
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class CacheConfig:
    """Cache configuration with type safety."""

    url: RedisDsn
    ttl: int = 3600  # Default 1 hour
    prefix: str = "recipe_value:"


@dataclass
class ServiceConfig:
    """Service-specific configuration."""

    name: str
    enabled: bool = True
    log_level: str = "INFO"
    timeout: int = 30
    retry_count: int = 3
    cache_enabled: bool = True


@dataclass
class RecipeConfig:
    """Recipe-related configuration."""

    min_quality_score: float = 0.6
    max_cooking_time: int = 180  # minutes
    supported_cuisines: Set[str] = frozenset(
        {
            "italian",
            "chinese",
            "mexican",
            "indian",
            "american",
            "japanese",
            "french",
            "thai",
            "mediterranean",
            "korean",
        }
    )
    difficulty_levels: Set[str] = frozenset({"easy", "medium", "hard"})


class Settings(BaseSettings):
    """Global application settings with type safety."""

    # Application
    app_name: str = "Recipe Value System"
    debug: bool = False
    environment: str = "development"
    log_config_path: Path = Path("config/logging_config.yaml")

    # Database
    database: DatabaseConfig
    cache: CacheConfig

    # Services
    services: Dict[str, ServiceConfig] = {}
    recipe: RecipeConfig = RecipeConfig()

    # Value calculation
    min_recipe_value: float = 1.0
    max_recipe_value: float = 100.0
    value_calculation_interval: int = 3600  # seconds

    # API
    api_timeout: int = 30
    api_rate_limit: int = 100
    api_token_expiry: int = 86400  # 24 hours

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """Load settings from configuration file and environment."""
    if config_path and config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
    else:
        config_data = {}

    return Settings(**config_data)


# Global settings instance
settings = load_settings()
