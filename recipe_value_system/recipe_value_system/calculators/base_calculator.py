"""Base calculator class for recipe value system."""
from abc import ABC, abstractmethod
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models.recipe import Recipe

class BaseCalculator(ABC):
    """Abstract base class for recipe value calculators."""
    
    def __init__(self, session: Optional[Session] = None):
        """Initialize calculator with optional database session.
        
        Args:
            session: Optional SQLAlchemy session for database operations
        """
        self.session = session
    
    @abstractmethod
    def calculate_value_metrics(self, recipe: Recipe) -> Dict[str, float]:
        """Calculate all value metrics for a recipe.
        
        Args:
            recipe: Recipe to analyze
            
        Returns:
            Dict of metric names to scores (all 0-1 scale)
        """
        pass
    
    def _validate_recipe(self, recipe: Recipe) -> bool:
        """Validate recipe has required attributes.
        
        Args:
            recipe: Recipe to validate
            
        Returns:
            True if recipe is valid, False otherwise
        """
        return bool(recipe and recipe.name and recipe.ingredients and recipe.steps)
    
    def _normalize_score(self, score: float, max_score: float = 6.0) -> float:
        """Normalize a score to 0-1 scale.
        
        Args:
            score: Raw score to normalize
            max_score: Maximum possible score, defaults to 6.0
            
        Returns:
            Normalized score between 0 and 1
        """
        if score <= 0 or max_score <= 0:
            return 0.0
        return min(1.0, score / max_score)
    
    def _calculate_average(self, values: list[float]) -> float:
        """Calculate average of a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Average value, or 0.0 if list is empty
        """
        if not values:
            return 0.0
        return sum(values) / len(values)
