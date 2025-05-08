"""Analytics package for Recipe Value System.

This package provides analytics and metrics collection services including:
- Feature usage tracking
- Value metrics analysis
- ROI calculations
- Business insights generation
"""

from .analytics_service import AnalyticsService
from .api import app as analytics_api
from .feature_catalog import FeatureCatalog
from .generate_insights import InsightGenerator
from .visualization import plot_value_radar

__all__ = [
    'AnalyticsService',
    'analytics_api',
    'FeatureCatalog',
    'InsightGenerator',
    'plot_value_radar',
]
