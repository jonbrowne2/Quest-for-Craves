from datetime import datetime
from typing import Dict, List, Optional


class Recipe:
    """A recipe with votes and history."""

    def __init__(
        self,
        name: str,
        ingredients: List[str],
        steps: List[str],
        prep_time: int,
        cook_time: int,
    ):
        self.name = name
        self.ingredients = ingredients
        self.steps = steps
        self.prep_time = prep_time  # Minutes
        self.cook_time = cook_time  # Minutes
        self.votes: Dict[str, List[int]] = {
            "taste": [],
            "health": [],
            "quick": [],
            "cheap": [],
            "easy": [],
        }
        self.last_made: Optional[datetime] = None

    def add_vote(
        self, taste: int, health: int, quick: int, cheap: int, easy: int
    ) -> None:
        """Add a vote (0-6 scale)."""
        for score in (taste, health, quick, cheap, easy):
            if not 0 <= score <= 6:
                raise ValueError("Scores must be 0-6")
        self.votes["taste"].append(taste)
        self.votes["health"].append(health)
        self.votes["quick"].append(quick)
        self.votes["cheap"].append(cheap)
        self.votes["easy"].append(easy)

    def mark_made(self) -> None:
        """Mark recipe as made today."""
        self.last_made = datetime.now()

    @property
    def mob_score(self) -> float | None:
        """Basic Mob Score: (taste + health) / (quick + cheap + easy)."""
        if not self.votes["taste"]:
            return None
        avg = {k: sum(v) / len(v) for k, v in self.votes.items()}
        return (avg["taste"] + avg["health"]) / (
            avg["quick"] + avg["cheap"] + avg["easy"]
        )
