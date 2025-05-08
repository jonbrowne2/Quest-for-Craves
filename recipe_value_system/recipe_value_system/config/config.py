"""Configuration module for the Recipe Value System and its components."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Try to import environment-specific config
try:
    from .env_config import get_database_url, load_environment_config
except ImportError:
    # For testing or standalone use
    def load_environment_config(env_name: Optional[str] = None) -> Dict[str, Any]:
        """Load environment configuration."""
        return {}

    def get_database_url(config: Dict[str, Any]) -> str:
        """Get database URL."""
        return "sqlite:///test.db"


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    url: str = Field(default="sqlite:///vault/recipes.db", description="Database URL")
    echo: bool = Field(default=False, description="Enable database echo")
    pool_size: int = Field(default=5, description="Database pool size")
    max_overflow: int = Field(default=10, description="Database max overflow")


class RedisConfig(BaseModel):
    """Redis configuration settings."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database")
    password: Optional[str] = Field(default=None, description="Redis password")


class MLConfig(BaseModel):
    """Machine learning configuration settings."""

    model_path: Path = Field(default=Path("models"), description="Model path")
    training_epochs: int = Field(default=100, description="Training epochs")
    batch_size: int = Field(default=32, description="Batch size")
    learning_rate: float = Field(default=0.001, description="Learning rate")

    model_config: Dict[str, Any] = Field(
        default={"protected_namespaces": ()}, description="Model configuration"
    )


class SystemConfig(BaseModel):
    """System configuration settings."""

    # Basic settings
    app_name: str = Field(default="Recipe Value System", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    env: str = Field(default="development", description="Environment name")

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )

    # Database
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig, description="Database configuration"
    )

    # Redis
    redis: RedisConfig = Field(
        default_factory=RedisConfig, description="Redis cache configuration"
    )

    # Machine Learning
    ml: MLConfig = Field(
        default_factory=MLConfig, description="Machine learning configuration"
    )

    # Recipe Value System specific
    weight_update_threshold: float = Field(
        default=0.1, description="Weight update threshold"
    )
    min_confidence_score: float = Field(
        default=0.6, description="Minimum confidence score"
    )
    cache_ttl: int = Field(default=3600, description="Cache TTL")
    max_recipes_per_page: int = Field(
        default=20, description="Maximum recipes per page"
    )

    # Internal storage for environment config (not validated by pydantic)
    env_config: Dict[str, Any] = Field(
        default_factory=dict, exclude=True, description="Environment configuration"
    )

    model_config: Dict[str, Any] = Field(
        default={"extra": "allow", "protected_namespaces": ()},
        description="Model configuration",
    )

    @model_validator(mode="after")
    def load_environment_config(self) -> "SystemConfig":
        """Load environment-specific configuration.

        Returns:
            Updated SystemConfig instance
        """
        self.env_config = load_environment_config(self.env)
        if self.env_config:
            # Update database URL if provided
            db_url = get_database_url(self.env_config)
            if db_url:
                self.database.url = db_url

            # Update other settings from environment config
            for key, value in self.env_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

        return self

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if hasattr(self, key):
            return getattr(self, key)

        return default


def get_config(environment: str = "development") -> SystemConfig:
    """Get system configuration for the specified environment.

    Args:
        environment: Target environment (development, staging, production)

    Returns:
        SystemConfig instance for the specified environment

    Raises:
        ValueError: If environment is invalid
    """
    if environment not in ["development", "staging", "production"]:
        raise ValueError(f"Invalid environment: {environment}")

    config_map: Dict[str, SystemConfig] = {
        "development": SystemConfig(
            debug_mode=True,
            log_level="DEBUG",
            data_dir="data/dev",
        ),
        "staging": SystemConfig(
            debug_mode=True,
            log_level="INFO",
            data_dir="data/staging",
        ),
        "production": SystemConfig(
            debug_mode=False,
            log_level="WARNING",
            data_dir="data/prod",
        ),
    }

    return config_map[environment]
