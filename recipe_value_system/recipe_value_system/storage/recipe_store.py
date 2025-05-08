"""Simple JSON storage for recipes with type safety."""
import json
import os
from datetime import datetime
from typing import List, Dict

from ..models.recipe import Recipe

class RecipeStore:
    """Handles persistent storage of recipes using JSON."""
    
    def __init__(self, storage_path: str = "recipes.json"):
        """Initialize recipe storage.
        
        Args:
            storage_path: Path to JSON storage file
        """
        self.storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """Create storage file if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            self.save_recipes([])
    
    def load_recipes(self) -> List[Recipe]:
        """Load recipes from storage.
        
        Returns:
            List of Recipe objects
        """
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return [
                    Recipe(
                        name=r["name"],
                        description=r["description"],
                        ingredients=r["ingredients"],
                        steps=r["steps"],
                        created_at=datetime.fromisoformat(r["created_at"])
                    ) for r in data
                ]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_recipes(self, recipes: List[Recipe]) -> None:
        """Save recipes to storage.
        
        Args:
            recipes: List of Recipe objects to save
        """
        data = [
            {
                "name": recipe.name,
                "description": recipe.description,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
                "created_at": recipe.created_at.isoformat(),
                "votes": recipe.votes,
                "rating": recipe.rating,
                "complexity": recipe.complexity,
                "mob_score": recipe.mob_score,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time
            }
            for recipe in recipes
        ]
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
