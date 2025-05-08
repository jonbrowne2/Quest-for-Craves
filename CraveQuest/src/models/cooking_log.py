"""Track user's cooking history and recipe interactions."""
from datetime import datetime
from typing import List, Optional

class UserCookingHistory:
    """Track when a user cooks recipes and their feedback."""
    def __init__(self, user):
        self.user = user
        self.history: List[dict] = []  # List of cooking sessions

    def log_cook(self, recipe, taste: str, cleanup: str) -> None:
        """Log a cooking session with feedback."""
        session = {
            "recipe_name": recipe.name,
            "date": datetime.now(),
            "taste": taste,
            "cleanup": cleanup
        }
        self.history.append(session)
        recipe.add_feedback(taste, cleanup)
        recipe.mark_made()
        self.user.adjust_coefficients(recipe, taste, cleanup)

    def get_last_cook(self) -> Optional[dict]:
        """Get the most recent cooking session."""
        return self.history[-1] if self.history else None

    def get_recipe_cooks(self, recipe_name: str) -> List[dict]:
        """Get all cooking sessions for a specific recipe."""
        return [s for s in self.history if s["recipe_name"] == recipe_name]

    def get_taste_distribution(self) -> dict:
        """Get distribution of taste ratings."""
        dist = {}
        for session in self.history:
            taste = session["taste"]
            dist[taste] = dist.get(taste, 0) + 1
        return dist

    def get_cleanup_distribution(self) -> dict:
        """Get distribution of cleanup ratings."""
        dist = {}
        for session in self.history:
            cleanup = session["cleanup"]
            dist[cleanup] = dist.get(cleanup, 0) + 1
        return dist
