from datetime import datetime
from typing import List, Optional

from ..constants import SCORE_LEVELS, CLEANUP_LEVELS

class Recipe:
    """A recipe with taste votes, calculated value factors, and ownership."""
    def __init__(self, name: str, ingredients: List[str], steps: List[str], 
                 prep_time: int, cook_time: int, servings: int, owner: str = "Unknown"):
        self.name = name
        self.ingredients = ingredients
        self.steps = steps
        self.prep_time = prep_time  # Minutes
        self.cook_time = cook_time  # Minutes
        self.servings = servings
        self.owner = owner  # "As made famous by [Creator] at [Site]" or user name
        self.votes: List[str] = []  # Taste ranks
        self.cleanups: List[str] = []  # Cleanup ranks
        self.last_made: Optional[datetime] = None
        self.made_count: int = 0
        self.health_rating: str = "Unknown"
        self.macros_fit: str = "Unknown"
        self.difficulty: float = len(steps) / 2

    def add_feedback(self, taste: str, cleanup: str) -> None:
        if taste not in SCORE_LEVELS:
            raise ValueError(f"Taste must be one of {list(SCORE_LEVELS.keys())}")
        if cleanup not in CLEANUP_LEVELS:
            raise ValueError(f"Cleanup must be one of {list(CLEANUP_LEVELS.keys())}")
        self.votes.append(taste)
        self.cleanups.append(cleanup)

    def mark_made(self) -> None:
        self.last_made = datetime.now()
        self.made_count += 1

    def calculate_value(self, user) -> float:
        if not self.votes:
            return 0.0
        coeffs = user.coefficients
        taste_avg = sum(list(SCORE_LEVELS.keys()).index(v) + 1 for v in self.votes) / len(self.votes)
        cleanup_avg = sum(list(CLEANUP_LEVELS.keys()).index(c) + 1 for c in self.cleanups) / len(self.cleanups)

        skill_map = {"Beginner": 4, "Home Cook": 2, "Chef": 1}
        skill_factor = skill_map.get(user.cook_ability, 2)
        familiarity = max(1, 4 - self.made_count)
        risk = max(1, min(4, (skill_factor + min(4, self.difficulty / 2) + familiarity - 1) / 3))

        time_per_serving = (self.prep_time + self.cook_time) / self.servings
        time = 1 if time_per_serving <= 20 else 2 if time_per_serving <= 45 else 3 if time_per_serving <= 90 else 4

        step_factor = min(4, len(self.steps) / 3)
        effort = max(1, min(4, (step_factor + cleanup_avg - 1) / 2))

        ingred_factor = min(4, len(self.ingredients) / self.servings / 2)
        sacrifice = max(1, ingred_factor)

        denominator = (coeffs["C_risk"] * risk) * (coeffs["C_time"] * time) * \
                      (coeffs["C_effort"] * effort) * (coeffs["C_sacrifice"] * sacrifice)
        return (coeffs["C_taste"] * taste_avg) / denominator

    def has_allergy_or_dislike(self, user) -> bool:
        ingredients_lower = " ".join(self.ingredients).lower()
        return any(a.lower() in ingredients_lower for a in user.allergies) or \
               any(d.lower() in ingredients_lower for d in user.dislikes)

    def get_grocery_list(self) -> List[str]:
        """Generate a basic grocery list from ingredients."""
        return self.ingredients.copy()  # Simple for MVP, refine later
