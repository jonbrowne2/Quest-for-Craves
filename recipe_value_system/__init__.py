"""Recipe Value System - A comprehensive recipe management and recommendation platform.

This package provides tools for recipe analysis, value calculation, and recommendation
based on user preferences, health metrics, and taste profiles.
"""

from .analytics import RecipeTrendAnalyzer
from .config import SystemConfig
from .models import Base, Recipe
from .value import UnifiedValueCalculator

__version__ = "1.0.0"
