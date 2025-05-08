"""Recipe model with SQLAlchemy mappings."""
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import JSON, DateTime, Integer, String, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class Recipe(Base):
    """Recipe model with value metrics."""
    
    __tablename__ = "recipes"
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_recipes_name", "name"),  # Name lookups
        Index("ix_recipes_created_at", "created_at"),  # Time-based queries
        Index("ix_recipes_rating", "rating"),  # Rating-based sorting
        Index("ix_recipes_mob_score", "mob_score"),  # Mob score sorting
    )
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Basic recipe info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    ingredients: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    steps: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Time tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    prep_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Vote tracking
    votes: Mapped[Dict[str, List[int]]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "taste": [],
            "health": [],
            "quick": [],
            "cheap": [],
            "easy": []
        }
    )
    
    # Calculated metrics
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    complexity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mob_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    def __init__(
        self,
        name: str,
        description: str = "",
        ingredients: Optional[List[str]] = None,
        steps: Optional[List[str]] = None,
        prep_time: Optional[int] = None,
        cook_time: Optional[int] = None,
        votes: Optional[Dict[str, List[int]]] = None,
        rating: Optional[float] = None,
        complexity: Optional[float] = None,
        mob_score: Optional[float] = None
    ) -> None:
        """Initialize a recipe.
        
        Args:
            name: Recipe name
            description: Recipe description
            ingredients: List of ingredients
            steps: List of preparation steps
            prep_time: Preparation time in minutes
            cook_time: Cooking time in minutes
            votes: Dictionary of vote lists by metric
            rating: Overall rating score
            complexity: Overall complexity score
            mob_score: Overall mob score
        """
        self.name = name
        self.description = description
        self.ingredients = ingredients or []
        self.steps = steps or []
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.votes = votes or {
            "taste": [],
            "health": [],
            "quick": [],
            "cheap": [],
            "easy": []
        }
        self.rating = rating
        self.complexity = complexity
        self.mob_score = mob_score
    
    def get_total_time(self) -> int:
        """Get total recipe time in minutes.
        
        Returns:
            Total time (prep + cook) in minutes, or 0 if times not set
        """
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook
    
    def add_vote(
        self,
        taste: int,
        health: int,
        quick: int,
        cheap: int,
        easy: int
    ) -> None:
        """Add votes for all metrics.
        
        Args:
            taste: Taste rating (0-6)
            health: Health rating (0-6)
            quick: Speed rating (0-6)
            cheap: Cost rating (0-6)
            easy: Ease rating (0-6)
        """
        self.votes["taste"].append(taste)
        self.votes["health"].append(health)
        self.votes["quick"].append(quick)
        self.votes["cheap"].append(cheap)
        self.votes["easy"].append(easy)
        
        # Update calculated metrics
        self._update_metrics()
    
    def _update_metrics(self) -> None:
        """Update calculated metrics based on votes."""
        if not self.votes["taste"]:  # No votes yet
            return
            
        # Calculate rating (taste and health)
        avg_taste = sum(self.votes["taste"]) / len(self.votes["taste"])
        avg_health = sum(self.votes["health"]) / len(self.votes["health"])
        self.rating = round(avg_taste * 0.6 + avg_health * 0.4, 2)
        
        # Calculate complexity (speed, cost, ease)
        avg_quick = sum(self.votes["quick"]) / len(self.votes["quick"])
        avg_cheap = sum(self.votes["cheap"]) / len(self.votes["cheap"])
        avg_easy = sum(self.votes["easy"]) / len(self.votes["easy"])
        self.complexity = round((avg_quick + avg_cheap + avg_easy) / 3, 2)
        
        # Calculate mob score (weighted average of all metrics)
        all_votes = []
        for votes in self.votes.values():
            all_votes.extend(votes)
        self.mob_score = round(sum(all_votes) / len(all_votes), 2)
