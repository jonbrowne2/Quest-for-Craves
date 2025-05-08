from typing import List, Dict
import json
import os

from ..constants import SCORE_LEVELS, CLEANUP_LEVELS

class User:
    """User profile with preferences and coefficients."""
    def __init__(self):
        self.cook_ability: str = "Home Cook"  # Beginner, Home Cook, Chef
        self.novelty_push: float = 0.5  # 0-1
        self.nostalgia_sensitivity: float = 0.5  # 0-1
        self.allergies: List[str] = []
        self.likes: List[str] = []
        self.dislikes: List[str] = []
        self.coefficients: Dict[str, float] = {
            "C_taste": 1.0, "C_risk": 1.0, "C_time": 1.0, "C_effort": 1.0, "C_sacrifice": 1.0
        }

    def save(self, filename: str = "data/user.json") -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data = {
            "cook_ability": self.cook_ability, "novelty_push": self.novelty_push,
            "nostalgia_sensitivity": self.nostalgia_sensitivity, "allergies": self.allergies,
            "likes": self.likes, "dislikes": self.dislikes, "coefficients": self.coefficients
        }
        try:
            with open(filename, "w") as f:
                json.dump(data, f)
            print(f"Saved user to {os.path.abspath(filename)}")
        except Exception as e:
            print(f"Failed to save user: {e}")

    @staticmethod
    def load(filename: str = "data/user.json") -> "User":
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            user = User()
            user.cook_ability = data["cook_ability"]
            user.novelty_push = data["novelty_push"]
            user.nostalgia_sensitivity = data["nostalgia_sensitivity"]
            user.allergies = data["allergies"]
            user.likes = data["likes"]
            user.dislikes = data["dislikes"]
            user.coefficients = data["coefficients"]
            print(f"Loaded user from {os.path.abspath(filename)}")
            return user
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"No user data found or invalid JSON ({e}), starting fresh")
            return User()

    def adjust_coefficients(self, recipe: "Recipe", taste_rank: str, cleanup_rank: str) -> None:
        """Adjust coefficients based on Taste and Cleanup ranks."""
        taste_idx = list(SCORE_LEVELS.keys()).index(taste_rank)  # 0-6
        cleanup_idx = list(CLEANUP_LEVELS.keys()).index(cleanup_rank)  # 0-3
        total_time = (recipe.prep_time + recipe.cook_time) / recipe.servings
        step_count = len(recipe.steps)
        ingred_per_serving = len(recipe.ingredients) / recipe.servings

        if taste_idx < 3:  # Below "Like"
            if total_time > 45:
                self.coefficients["C_time"] = max(0.1, self.coefficients["C_time"] - 0.1)
            if step_count > 10:
                self.coefficients["C_effort"] = max(0.1, self.coefficients["C_effort"] - 0.1)
            if ingred_per_serving > 5:
                self.coefficients["C_sacrifice"] = max(0.1, self.coefficients["C_sacrifice"] - 0.1)
            self.coefficients["C_taste"] = max(0.1, self.coefficients["C_taste"] - 0.05)
        elif taste_idx > 4:  # Above "Love"
            self.coefficients["C_taste"] = min(1.0, self.coefficients["C_taste"] + 0.05)

        if cleanup_idx > 1:  # Above "Light"
            self.coefficients["C_effort"] = max(0.1, self.coefficients["C_effort"] - 0.1)
