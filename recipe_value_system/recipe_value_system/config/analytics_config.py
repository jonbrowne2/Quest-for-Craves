"""Analytics configuration module."""

from datetime import timedelta
from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class AnalyticsThresholds(TypedDict):
    """Analytics threshold configuration."""

    min_value: float
    max_value: float
    warning_level: float
    critical_level: float


class MetricsConfig(BaseModel):
    """Configuration for analytics metrics."""

    enabled: bool = True
    sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    batch_size: int = Field(default=100, ge=1)
    timeout_ms: int = Field(default=5000, ge=0)
    retry_count: int = Field(default=3, ge=0)
    cache_ttl: timedelta = Field(default=timedelta(hours=1))


class AnalyticsConfig(BaseModel):
    """Main analytics configuration."""

    enabled: bool = True
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    thresholds: Dict[str, AnalyticsThresholds] = Field(
        default_factory=lambda: {
            "quality": {
                "min_value": 0.0,
                "max_value": 1.0,
                "warning_level": 0.3,
                "critical_level": 0.1,
            },
            "complexity": {
                "min_value": 0.0,
                "max_value": 1.0,
                "warning_level": 0.7,
                "critical_level": 0.9,
            },
            "performance": {
                "min_value": 0.0,
                "max_value": 1.0,
                "warning_level": 0.4,
                "critical_level": 0.2,
            },
        }
    )
    excluded_paths: List[str] = Field(default_factory=list)
    log_level: str = Field(default="INFO")

    def get_threshold(self, metric_name: str) -> Optional[AnalyticsThresholds]:
        """Get threshold configuration for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Threshold configuration if found
        """
        return self.thresholds.get(metric_name)

    def is_path_excluded(self, path: str) -> bool:
        """Check if a path is excluded from analytics.

        Args:
            path: Path to check

        Returns:
            True if path is excluded
        """
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    def update_thresholds(
        self, metric_name: str, thresholds: AnalyticsThresholds
    ) -> None:
        """Update threshold configuration for a metric.

        Args:
            metric_name: Name of the metric
            thresholds: New threshold configuration
        """
        self.thresholds[metric_name] = thresholds


# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "metrics": {
        "sample_rate": 0.5,
        "batch_size": 50,
        "timeout_ms": 1000,
        "retry_count": 1,
        "cache_ttl": timedelta(minutes=5),
    },
    "log_level": "DEBUG",
}

PRODUCTION_CONFIG = {
    "metrics": {
        "sample_rate": 1.0,
        "batch_size": 100,
        "timeout_ms": 5000,
        "retry_count": 3,
        "cache_ttl": timedelta(hours=1),
    },
    "log_level": "INFO",
}

TESTING_CONFIG = {
    "metrics": {
        "sample_rate": 0.1,
        "batch_size": 10,
        "timeout_ms": 500,
        "retry_count": 1,
        "cache_ttl": timedelta(minutes=1),
    },
    "log_level": "DEBUG",
}

# Analytics configuration instance
ANALYTICS: AnalyticsConfig = AnalyticsConfig()


def get_config(environment: str = "development") -> AnalyticsConfig:
    """Get environment-specific analytics configuration.

    Args:
        environment: Target environment

    Returns:
        Environment-specific analytics configuration
    """
    config = AnalyticsConfig()

    if environment == "development":
        for key, value in DEVELOPMENT_CONFIG.items():
            if key == "metrics":
                for metric_key, metric_value in value.items():
                    setattr(config.metrics, metric_key, metric_value)
            else:
                setattr(config, key, value)
    elif environment == "production":
        for key, value in PRODUCTION_CONFIG.items():
            if key == "metrics":
                for metric_key, metric_value in value.items():
                    setattr(config.metrics, metric_key, metric_value)
            else:
                setattr(config, key, value)
    elif environment == "testing":
        for key, value in TESTING_CONFIG.items():
            if key == "metrics":
                for metric_key, metric_value in value.items():
                    setattr(config.metrics, metric_key, metric_value)
            else:
                setattr(config, key, value)

    return config
