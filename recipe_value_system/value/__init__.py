"""Recipe Value System core module.

The value module provides tools and algorithms for calculating the overall value
of recipes based on multiple factors including taste, health, time, and effort.

This package provides functionality for calculating recipe values.
"""

from .calculator import (
    ComponentLearner,
    CostLearner,
    NutritionLearner,
    TasteLearner,
    TextureLearner,
)
from .calculator import UnifiedValueCalculator as ValueCalculator
from .calculator import ValueComponents as ValueCache
from .calculator import (
    ValueMode,
)
from .confidence import ConfidenceCalculator
from .context import ContextManager
from .learning import FeedbackLearner
from .quality import DataQualityMonitor

__all__ = [
    # Core calculator
    "ValueCalculator",
    # Value data structures
    "ValueCache",
    # Enums and constants
    "ValueMode",
    # Learners
    "ComponentLearner",
    "CostLearner",
    "NutritionLearner",
    "TasteLearner",
    "TextureLearner",
    # Support modules
    "ConfidenceCalculator",
    "ContextManager",
    "FeedbackLearner",
    "DataQualityMonitor",
]
