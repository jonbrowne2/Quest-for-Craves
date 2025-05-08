"""Configuration for data archival and retention policies."""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict


@dataclass
class ArchivalConfig:
    """Configuration for data archival policies."""

    # How long to keep detailed interaction data
    INTERACTION_RETENTION = timedelta(days=365)

    # How long to keep recommendation logs
    RECOMMENDATION_LOG_RETENTION = timedelta(days=90)

    # Aggregation periods for historical data
    AGGREGATION_PERIODS = {
        "hourly": timedelta(days=7),  # Keep hourly data for 1 week
        "daily": timedelta(days=90),  # Keep daily data for 3 months
        "weekly": timedelta(days=365),  # Keep weekly data for 1 year
        "monthly": timedelta(days=730),  # Keep monthly data for 2 years
    }

    # Partition rotation schedule
    PARTITION_ROTATION = {
        "user_recipe_interactions": timedelta(days=30),  # Monthly partitions
        "recommendation_logs": timedelta(days=30),
        "user_feedback": timedelta(days=90),
    }

    @classmethod
    def get_aggregation_config(cls) -> Dict[str, Any]:
        """Get configuration for data aggregation jobs."""
        return {
            "interaction_metrics": {
                "dimensions": ["recipe_id", "user_id", "interaction_type"],
                "metrics": ["count", "avg_rating", "success_rate"],
                "periods": cls.AGGREGATION_PERIODS,
            },
            "recipe_metrics": {
                "dimensions": ["recipe_id", "cuisine_type", "difficulty_level"],
                "metrics": ["view_count", "avg_rating", "completion_rate"],
                "periods": cls.AGGREGATION_PERIODS,
            },
        }
