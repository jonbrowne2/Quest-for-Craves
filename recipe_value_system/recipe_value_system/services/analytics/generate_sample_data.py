"""Generate sample analytics data for testing and development.

This module provides functions to generate realistic sample data for testing the
analytics system. It creates events, feature usage data, and value metrics that
mimic real user behavior patterns.
"""

from __future__ import annotations

import datetime
import random
import uuid
from typing import Any, Dict, List

from .analytics_service import AnalyticsService

# Initialize analytics service
analytics = AnalyticsService()

# Sample user IDs (100 users)
USER_IDS: List[str] = [f"user_{i}" for i in range(1, 101)]

# Sample recipe IDs (50 recipes)
RECIPE_IDS: List[str] = [f"recipe_{i}" for i in range(1, 51)]

# Event types with their descriptions
EVENT_TYPES: List[str] = [
    "recipe_view",  # User viewed a recipe
    "recipe_search",  # User performed a recipe search
    "recipe_filter",  # User filtered recipe results
    "recipe_rate",  # User rated a recipe
    "recipe_favorite",  # User favorited a recipe
    "recipe_cook",  # User marked recipe as cooked
    "recipe_share",  # User shared a recipe
    "recipe_print",  # User printed a recipe
    "category_view",  # User viewed a recipe category
    "variant_view",  # User viewed a recipe variant
    "similar_recipe_click",  # User clicked on similar recipe
]

# Features by category
FEATURES: Dict[str, List[str]] = {
    "core": ["recipe_view", "recipe_search", "recipe_filter", "recipe_rating"],
    "growth": ["recipe_variant", "ai_companion", "similar_recipes"],
    "legacy": ["old_print", "text_only_view"],
    "premium": ["ai_video", "cookbook_export", "meal_planning"],
}

# Value metrics with descriptions
VALUE_METRICS: List[str] = [
    "recipe_satisfaction",  # User satisfaction with recipes
    "feature_satisfaction",  # User satisfaction with features
    "nps",  # Net Promoter Score
]


def random_date(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
) -> datetime.datetime:
    """Generate a random date between start_date and end_date.

    Args:
        start_date: The earliest possible date
        end_date: The latest possible date

    Returns:
        A random datetime between start_date and end_date
    """
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)


def generate_event_data(event_type: str) -> Dict[str, Any]:
    """Generate random data for an event.

    Args:
        event_type: The type of event to generate data for

    Returns:
        Dictionary containing the generated event data
    """
    user_id = random.choice(USER_IDS)
    recipe_id = random.choice(RECIPE_IDS)
    timestamp = random_date(
        datetime.datetime.now() - datetime.timedelta(days=30),
        datetime.datetime.now(),
    )

    base_data = {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_type": event_type,
        "timestamp": timestamp.isoformat(),
        "recipe_id": recipe_id,
    }

    # Add event-specific data
    if event_type == "recipe_rate":
        base_data["rating"] = random.randint(1, 5)
    elif event_type == "recipe_search":
        base_data["search_term"] = random.choice(
            ["pasta", "chicken", "vegan", "quick", "healthy"]
        )
    elif event_type == "recipe_filter":
        base_data["filters"] = random.choice(
            [
                ["vegetarian", "quick"],
                ["gluten-free"],
                ["low-carb", "high-protein"],
            ]
        )

    return base_data


def generate_feature_usage_data(
    feature_name: str,
    category: str,
) -> Dict[str, Any]:
    """Generate random data for feature usage.

    Args:
        feature_name: Name of the feature
        category: Category the feature belongs to

    Returns:
        Dictionary containing the generated feature usage data
    """
    user_id = random.choice(USER_IDS)
    timestamp = random_date(
        datetime.datetime.now() - datetime.timedelta(days=30),
        datetime.datetime.now(),
    )

    return {
        "usage_id": str(uuid.uuid4()),
        "user_id": user_id,
        "feature_name": feature_name,
        "category": category,
        "timestamp": timestamp.isoformat(),
        "duration_seconds": random.randint(10, 300),
        "successful": random.random() > 0.1,  # 90% success rate
        "error": None if random.random() > 0.1 else "timeout",
    }


def generate_value_metric_data(metric_name: str) -> Dict[str, Any]:
    """Generate random data for value metrics.

    Args:
        metric_name: Name of the metric to generate data for

    Returns:
        Dictionary containing the generated value metric data
    """
    user_id = random.choice(USER_IDS)
    timestamp = random_date(
        datetime.datetime.now() - datetime.timedelta(days=30),
        datetime.datetime.now(),
    )

    base_data = {
        "metric_id": str(uuid.uuid4()),
        "user_id": user_id,
        "metric_name": metric_name,
        "timestamp": timestamp.isoformat(),
    }

    if metric_name == "recipe_satisfaction":
        base_data.update(
            {
                "recipe_id": random.choice(RECIPE_IDS),
                "satisfaction_score": random.randint(1, 5),
                "would_cook_again": random.random() > 0.2,  # 80% would cook again
                "comments": random.choice(
                    [
                        "Great recipe!",
                        "Too complicated",
                        "Family loved it",
                        "Missing details",
                        None,
                    ]
                ),
            }
        )
    elif metric_name == "feature_satisfaction":
        base_data.update(
            {
                "feature_name": random.choice(
                    [item for sublist in FEATURES.values() for item in sublist]
                ),
                "satisfaction_score": random.randint(1, 5),
                "ease_of_use": random.randint(1, 5),
            }
        )
    elif metric_name == "nps":
        base_data.update(
            {
                "score": random.randint(0, 10),
                "feedback": random.choice(
                    [
                        "Love the app!",
                        "Need more features",
                        "UI could be better",
                        "Very helpful",
                        None,
                    ]
                ),
            }
        )

    return base_data


def generate_sample_data(
    num_events: int = 1000,
    num_feature_usages: int = 500,
    num_value_metrics: int = 300,
) -> None:
    """Generate sample data for testing.

    Args:
        num_events: Number of events to generate
        num_feature_usages: Number of feature usage records to generate
        num_value_metrics: Number of value metric records to generate
    """
    # Generate events
    for _ in range(num_events):
        event_type = random.choice(EVENT_TYPES)
        event_data = generate_event_data(event_type)
        analytics.track_event(event_data)

    # Generate feature usage data
    for _ in range(num_feature_usages):
        category = random.choice(list(FEATURES.keys()))
        feature = random.choice(FEATURES[category])
        usage_data = generate_feature_usage_data(feature, category)
        analytics.track_feature_usage(usage_data)

    # Generate value metrics
    for _ in range(num_value_metrics):
        metric = random.choice(VALUE_METRICS)
        metric_data = generate_value_metric_data(metric)
        analytics.track_value_metric(metric_data)


if __name__ == "__main__":
    generate_sample_data()
