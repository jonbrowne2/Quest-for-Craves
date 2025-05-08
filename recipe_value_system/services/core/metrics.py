"""Type-safe metrics collection system."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

from prometheus_client import Counter, Gauge, Histogram, Summary

from ...config.settings import settings


class MetricType(Enum):
    """Types of metrics supported."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricDefinition:
    """Definition of a metric."""

    name: str
    type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # For histograms


@dataclass
class MetricValue:
    """Value of a metric at a point in time."""

    name: str
    value: Union[int, float]
    labels: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MetricsManager:
    """Type-safe metrics management system."""

    def __init__(self) -> None:
        """Initialize metrics manager."""
        self._metrics: Dict[str, Union[Counter, Gauge, Histogram, Summary]] = {}
        self._definitions: Dict[str, MetricDefinition] = {}
        self._setup_default_metrics()

    def _setup_default_metrics(self) -> None:
        """Set up default system metrics."""
        # Service metrics
        self.register_metric(
            MetricDefinition(
                name="service_health_status",
                type=MetricType.GAUGE,
                description="Health status of services",
                labels=["service_name"],
            )
        )

        # Recipe metrics
        self.register_metric(
            MetricDefinition(
                name="recipe_quality_score",
                type=MetricType.HISTOGRAM,
                description="Distribution of recipe quality scores",
                labels=["cuisine_type"],
                buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            )
        )

        # User metrics
        self.register_metric(
            MetricDefinition(
                name="user_interaction_count",
                type=MetricType.COUNTER,
                description="Number of user interactions",
                labels=["interaction_type"],
            )
        )

        # Performance metrics
        self.register_metric(
            MetricDefinition(
                name="request_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="Request duration in seconds",
                labels=["endpoint"],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            )
        )

        # Database metrics
        self.register_metric(
            MetricDefinition(
                name="database_connection_pool",
                type=MetricType.GAUGE,
                description="Database connection pool status",
                labels=["status"],
            )
        )

    def register_metric(self, definition: MetricDefinition) -> None:
        """Register a new metric."""
        if definition.name in self._metrics:
            return

        self._definitions[definition.name] = definition

        if definition.type == MetricType.COUNTER:
            self._metrics[definition.name] = Counter(
                definition.name, definition.description, definition.labels
            )
        elif definition.type == MetricType.GAUGE:
            self._metrics[definition.name] = Gauge(
                definition.name, definition.description, definition.labels
            )
        elif definition.type == MetricType.HISTOGRAM:
            self._metrics[definition.name] = Histogram(
                definition.name,
                definition.description,
                definition.labels,
                buckets=definition.buckets or Histogram.DEFAULT_BUCKETS,
            )
        elif definition.type == MetricType.SUMMARY:
            self._metrics[definition.name] = Summary(
                definition.name, definition.description, definition.labels
            )

    def record_metric(self, value: MetricValue) -> None:
        """Record a metric value."""
        if value.name not in self._metrics:
            raise ValueError(f"Metric {value.name} not registered")

        metric = self._metrics[value.name]
        definition = self._definitions[value.name]

        if definition.type == MetricType.COUNTER:
            metric.labels(**value.labels).inc(value.value)
        elif definition.type == MetricType.GAUGE:
            metric.labels(**value.labels).set(value.value)
        elif definition.type == MetricType.HISTOGRAM:
            metric.labels(**value.labels).observe(value.value)
        elif definition.type == MetricType.SUMMARY:
            metric.labels(**value.labels).observe(value.value)

    def get_metric(
        self, name: str
    ) -> Optional[Union[Counter, Gauge, Histogram, Summary]]:
        """Get a metric by name."""
        return self._metrics.get(name)


# Metric decorators
def track_duration(metric_name: str, **labels: str):
    """Decorator to track function duration."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            result = func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()

            metrics_manager.record_metric(
                MetricValue(name=metric_name, value=duration, labels=labels)
            )

            return result

        return wrapper

    return decorator


def count_calls(metric_name: str, **labels: str):
    """Decorator to count function calls."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics_manager.record_metric(
                MetricValue(name=metric_name, value=1, labels=labels)
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Global metrics manager instance
metrics_manager = MetricsManager()
