"""FastAPI endpoints for analytics data collection and reporting.

This module provides REST API endpoints for:
1. Event tracking
2. Feature usage analytics
3. Value metrics collection
4. Feature registration and analysis
"""

import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .analytics_service import AnalyticsService

app = FastAPI(title="Recipe Value System Analytics API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analytics service
analytics_service = AnalyticsService()


# Pydantic models for request validation
class EventData(BaseModel):
    """Event data model for tracking analytics events.

    Attributes:
        eventType: Type of event being tracked
        eventData: Additional event metadata and context
    """

    eventType: str
    eventData: Dict[str, Any]


class FeatureUsageData(BaseModel):
    """Feature usage data model for tracking feature interactions.

    Attributes:
        feature: Name of the feature being used
        data: Additional usage metadata and context
    """

    feature: str
    data: Dict[str, Any]


class ValueMetricData(BaseModel):
    """Value metric data model for tracking user satisfaction and feedback.

    Attributes:
        metric: Name of the metric being tracked
        data: Additional metric data and context
    """

    metric: str
    data: Dict[str, Any]


class FeatureRegistration(BaseModel):
    """Feature registration model for adding new features to track.

    Attributes:
        featureName: Name of the feature to register
        category: Category of the feature (core, growth, legacy, premium)
        description: Description of the feature's purpose
        data: Optional additional feature metadata
    """

    featureName: str
    category: str
    description: str
    data: Optional[Dict[str, Any]] = None


class DateRange(BaseModel):
    """Date range model for filtering analytics data.

    Attributes:
        startDate: Optional start date for the date range
        endDate: Optional end date for the date range
    """

    startDate: Optional[datetime.datetime] = None
    endDate: Optional[datetime.datetime] = None


# API endpoints
@app.post("/api/analytics/events")
async def track_event(event_data: EventData):
    """Track an analytics event.

    Args:
        event_data: Event data containing type and metadata

    Returns:
        Dict containing success status and event ID

    Raises:
        HTTPException: If event tracking fails
    """
    try:
        user_id = event_data.eventData.get("userId", "anonymous")
        event_id = analytics_service.track_event(
            event_data.eventType,
            user_id,
            event_data.eventData,
        )
        return {"success": True, "eventId": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analytics/feature-usage")
async def track_feature_usage(usage_data: FeatureUsageData):
    """Track feature usage start or completion.

    Args:
        usage_data: Feature usage data containing feature info and context

    Returns:
        Dict containing success status and tracking ID

    Raises:
        HTTPException: If usage tracking fails or required data is missing
    """
    try:
        user_id = usage_data.data.get("userId", "anonymous")
        category = usage_data.data.get("category", "core")

        # Check if this is a completion event
        if usage_data.data.get("action") == "complete":
            feature_usage_id = usage_data.data.get("trackingId")
            if not feature_usage_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing trackingId for completion event",
                )

            completed = usage_data.data.get("completed", False)
            time_spent = usage_data.data.get("timeSpent", 0)
            abandonment_point = usage_data.data.get("abandonmentPoint")

            success = analytics_service.complete_feature_usage(
                feature_usage_id,
                completed,
                time_spent,
                abandonment_point,
                usage_data.data,
            )
            return {"success": success}

        # This is a start event
        feature_usage_id = analytics_service.track_feature_usage(
            usage_data.feature,
            user_id,
            category,
            usage_data.data,
        )
        return {"success": True, "featureUsageId": feature_usage_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analytics/value-metrics")
async def track_value_metric(metric_data: ValueMetricData):
    """Track a value metric for measuring user satisfaction.

    Args:
        metric_data: Value metric data containing scores and feedback

    Returns:
        Dict containing success status and metric ID

    Raises:
        HTTPException: If metric tracking fails
    """
    try:
        user_id = metric_data.data.get("userId", "anonymous")
        score = metric_data.data.get("score")
        recipe_id = metric_data.data.get("recipeId")
        feature_id = metric_data.data.get("featureId")
        feedback = metric_data.data.get("feedback")

        metric_id = analytics_service.track_value_metric(
            metric_data.metric,
            user_id,
            score,
            recipe_id,
            feature_id,
            feedback,
            metric_data.data,
        )
        return {"success": True, "metricId": metric_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analytics/features")
async def register_feature(feature_data: FeatureRegistration):
    """Register a new feature for tracking.

    Args:
        feature_data: Feature registration data with metadata

    Returns:
        Dict containing success status and feature ID

    Raises:
        HTTPException: If feature registration fails
    """
    try:
        feature_id = analytics_service.register_feature(
            feature_data.featureName,
            feature_data.category,
            feature_data.description,
            feature_data.data,
        )
        return {"success": True, "featureId": feature_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/features")
async def get_features():
    """Get all registered features grouped by category.

    Returns:
        Dict mapping categories to lists of feature metadata

    Raises:
        HTTPException: If feature retrieval fails
    """
    try:
        features = analytics_service.get_feature_categories()
        return features
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/features/{feature_name}/stats")
async def get_feature_stats(
    feature_name: str,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
):
    """Get usage statistics for a specific feature.

    Args:
        feature_name: Name of the feature to get stats for
        start_date: Optional start date for filtering stats
        end_date: Optional end date for filtering stats

    Returns:
        Dict containing feature usage statistics

    Raises:
        HTTPException: If stats retrieval fails
    """
    try:
        stats = analytics_service.get_feature_usage_stats(
            feature_name,
            start_date,
            end_date,
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/features/{feature_name}/roi")
async def get_feature_roi(
    feature_name: str,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
):
    """Get ROI analysis for a specific feature.

    Args:
        feature_name: Name of the feature to analyze
        start_date: Optional start date for analysis period
        end_date: Optional end date for analysis period

    Returns:
        Dict containing ROI analysis results

    Raises:
        HTTPException: If ROI analysis fails
    """
    try:
        roi = analytics_service.analyze_feature_roi(
            feature_name,
            start_date,
            end_date,
        )
        return roi
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/metrics/{metric_name}/stats")
async def get_metric_stats(
    metric_name: str,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
):
    """Get statistics for a specific value metric.

    Args:
        metric_name: Name of the metric to get stats for
        start_date: Optional start date for filtering stats
        end_date: Optional end date for filtering stats

    Returns:
        Dict containing metric statistics

    Raises:
        HTTPException: If stats retrieval fails
    """
    try:
        stats = analytics_service.get_value_metric_stats(
            metric_name,
            start_date,
            end_date,
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
