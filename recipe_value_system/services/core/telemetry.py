"""Type-safe telemetry system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from ...config.settings import settings
from .metrics import MetricValue, metrics_manager


@dataclass
class SpanContext:
    """Context for a telemetry span."""

    operation_name: str
    service_name: str
    start_time: datetime = field(default_factory=datetime.utcnow)
    attributes: Dict[str, str] = field(default_factory=dict)
    parent_id: Optional[str] = None


@dataclass
class TelemetryEvent:
    """Telemetry event data."""

    name: str
    timestamp: datetime
    level: str  # info, warning, error
    attributes: Dict[str, str]
    measurements: Dict[str, Union[int, float]] = field(default_factory=dict)


class TelemetryManager:
    """Type-safe telemetry management system."""

    def __init__(self) -> None:
        """Initialize telemetry manager."""
        self._setup_tracing()
        self._events: List[TelemetryEvent] = []

    def _setup_tracing(self) -> None:
        """Set up OpenTelemetry tracing."""
        resource = Resource.create(
            {"service.name": settings.app_name, "environment": settings.environment}
        )

        trace.set_tracer_provider(TracerProvider(resource=resource))

        # Set up OTLP exporter
        otlp_exporter = OTLPSpanExporter()
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        self.tracer = trace.get_tracer(__name__)

    def create_span(self, context: SpanContext) -> trace.Span:
        """Create a new telemetry span."""
        with self.tracer.start_as_current_span(
            context.operation_name,
            attributes={"service.name": context.service_name, **context.attributes},
        ) as span:
            # Record start time metric
            metrics_manager.record_metric(
                MetricValue(
                    name="operation_start_time",
                    value=context.start_time.timestamp(),
                    labels={
                        "operation": context.operation_name,
                        "service": context.service_name,
                    },
                )
            )
            return span

    def record_event(self, event: TelemetryEvent) -> None:
        """Record a telemetry event."""
        self._events.append(event)

        # Record event metric
        metrics_manager.record_metric(
            MetricValue(
                name="telemetry_event",
                value=1,
                labels={"event_name": event.name, "level": event.level},
            )
        )

        # Record measurements as separate metrics
        for name, value in event.measurements.items():
            metrics_manager.record_metric(
                MetricValue(
                    name=f"event_measurement_{name}",
                    value=value,
                    labels={"event_name": event.name, "level": event.level},
                )
            )

    def get_recent_events(
        self, level: Optional[str] = None, limit: int = 100
    ) -> List[TelemetryEvent]:
        """Get recent telemetry events."""
        events = self._events
        if level:
            events = [e for e in events if e.level == level]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]


# Telemetry decorators
def trace_operation(operation_name: str, **attributes: str):
    """Decorator to trace function execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            context = SpanContext(
                operation_name=operation_name,
                service_name=settings.app_name,
                attributes=attributes,
            )

            with telemetry_manager.create_span(context):
                start_time = datetime.utcnow()
                try:
                    result = func(*args, **kwargs)

                    # Record successful operation
                    telemetry_manager.record_event(
                        TelemetryEvent(
                            name=f"{operation_name}_success",
                            timestamp=datetime.utcnow(),
                            level="info",
                            attributes=attributes,
                            measurements={
                                "duration_ms": (
                                    datetime.utcnow() - start_time
                                ).total_seconds()
                                * 1000
                            },
                        )
                    )

                    return result
                except Exception as e:
                    # Record operation error
                    telemetry_manager.record_event(
                        TelemetryEvent(
                            name=f"{operation_name}_error",
                            timestamp=datetime.utcnow(),
                            level="error",
                            attributes={
                                **attributes,
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                            },
                        )
                    )
                    raise

        return wrapper

    return decorator


# Global telemetry manager instance
telemetry_manager = TelemetryManager()
