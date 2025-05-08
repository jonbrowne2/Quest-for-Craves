"""Value calculator for recipe metrics."""
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models.recipe import Recipe
from .base_calculator import BaseCalculator

class ValueCalculator(BaseCalculator):
    """Calculates various value metrics for recipes."""
    
    def __init__(self, session: Optional[Session] = None):
        """Initialize calculator with optional database session.
        
        Args:
            session: Optional SQLAlchemy session for future DB operations
        """
        super().__init__(session)
    
    def calculate_value_metrics(self, recipe: Recipe) -> Dict[str, float]:
        """Calculate all value metrics for a recipe.
        
        Args:
            recipe: Recipe to analyze
            
        Returns:
            Dict of metric names to scores (all 0-1 scale)
        """
        if not recipe.rating or not self._validate_recipe(recipe):
            return {
                "quality": 0.0,
                "complexity": 0.0,
                "rating": 0.0,
                "time_value": 0.0
            }
        
        return {
            "quality": self.calculate_quality_score(recipe),
            "complexity": self.calculate_complexity_score(recipe),
            "rating": self.calculate_rating_impact(recipe),
            "time_value": self.calculate_time_value(recipe)
        }
    
    def _calculate_completeness(self, recipe: Recipe) -> float:
        """Calculate recipe completeness factor.
        
        Returns:
            Score 0-1 based on recipe completeness
        """
        if not self._validate_recipe(recipe):
            return 0.0
            
        # Basic completeness checks
        has_description = bool(recipe.description.strip())
        has_ingredients = len(recipe.ingredients) >= 2  # At least 2 ingredients
        has_steps = len(recipe.steps) >= 2  # At least 2 steps
        has_times = recipe.prep_time is not None and recipe.cook_time is not None
        
        # Calculate completeness (equal weights)
        checks = [has_description, has_ingredients, has_steps, has_times]
        return sum(1 for check in checks if check) / len(checks)
    
    def calculate_quality_score(self, recipe: Recipe) -> float:
        """Calculate quality score based on rating and completeness.
        
        Returns:
            Score 0-1 representing overall quality
        """
        if not recipe.rating:
            return 0.0
            
        base_score = self._normalize_score(recipe.rating)
        completeness = self._calculate_completeness(recipe)
        return min(1.0, base_score * completeness)
    
    def calculate_complexity_score(self, recipe: Recipe) -> float:
        """Calculate complexity score based on speed, cost, and ease.
        
        Returns:
            Score 0-1 where higher means less complex
        """
        if not recipe.votes["quick"]:
            return 0.0
            
        # Get averages and normalize to 0-1
        quick_votes = recipe.votes["quick"]
        cheap_votes = recipe.votes["cheap"]
        easy_votes = recipe.votes["easy"]
        
        avg_quick = self._normalize_score(self._calculate_average(quick_votes))
        avg_cheap = self._normalize_score(self._calculate_average(cheap_votes))
        avg_easy = self._normalize_score(self._calculate_average(easy_votes))
        
        # Equal weights for complexity factors
        return (avg_quick + avg_cheap + avg_easy) / 3
    
    def calculate_rating_impact(self, recipe: Recipe) -> float:
        """Calculate rating impact based on rating and time value.
        
        Returns:
            Score 0-1 representing overall impact
        """
        if not recipe.rating:
            return 0.0
            
        base_impact = self._normalize_score(recipe.rating)
        time_factor = self.calculate_time_value(recipe)
        return min(1.0, base_impact * (1.0 + time_factor))
    
    def calculate_time_value(self, recipe: Recipe) -> float:
        """Calculate time value based on speed rating and total time.
        
        Returns:
            Score 0-1 representing value for time
        """
        if not recipe.votes["quick"]:
            return 0.0
            
        total_time = recipe.get_total_time()
        if total_time <= 0:
            return 0.0
            
        # Normalize quick score to 0-1
        quick_votes = recipe.votes["quick"]
        avg_quick = self._normalize_score(self._calculate_average(quick_votes))
        
        # Convert total_time to a 0-1 scale (lower is better)
        # Cap at 3 hours (180 minutes)
        time_factor = 1.0 - min(total_time / 180, 1.0)
        
        return (avg_quick + time_factor) / 2
