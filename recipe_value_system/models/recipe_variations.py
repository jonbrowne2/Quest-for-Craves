"""Models for tracking recipe variations and modifications."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast  # noqa: F401

from sqlalchemy import JSON  # noqa: F401
from sqlalchemy import Enum  # noqa: F401
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


class RecipeClusterType(enum.Enum):
    """Types of recipe clusters."""

    IDENTICAL = "identical"  # Same ingredients and instructions
    SIMILAR = "similar"  # Minor variations
    VARIANT = "variant"  # Significant variations but same core concept
    INSPIRED = "inspired"  # Inspired by but substantially different


class ModificationImpact(enum.Enum):
    """Impact of a recipe modification."""

    TEXTURE = "texture"
    TASTE = "taste"
    APPEARANCE = "appearance"
    NUTRITION = "nutrition"
    COST = "cost"
    DIFFICULTY = "difficulty"
    TIME = "time"


# Association table for recipe clusters
recipe_cluster_association = Table(
    "recipe_cluster_association",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("cluster_id", Integer, ForeignKey("recipe_clusters.id"), primary_key=True),
)


class RecipeCluster(Base, TimestampMixin):
    """Groups similar recipes together.

    This helps track variations of the same basic recipe concept,
    like different versions of chocolate chip cookies.
    """

    __tablename__ = "recipe_clusters"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(200))
    description: Optional[str] = Column(Text)
    core_ingredients: Dict[str, Any] = Column(JSONB)
    optional_ingredients: Dict[str, Any] = Column(JSONB)
    key_techniques: List[str] = Column(JSONB)
    avg_rating: Optional[float] = Column(Float)
    total_reviews: int = Column(Integer, default=0)
    popularity_score: Optional[float] = Column(Float)

    # Relationships
    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe", secondary=recipe_cluster_association, back_populates="clusters"
    )
    variations: Mapped[List["RecipeVariation"]] = relationship(
        "RecipeVariation", back_populates="cluster"
    )

    def calculate_similarity(self, recipe: "Recipe") -> float:
        """Calculate similarity score between this cluster and a recipe.

        Args:
            recipe: Recipe to compare against

        Returns:
            float: Similarity score between 0 and 1
        """
        # TODO: Implement similarity calculation
        return 0.0


class RecipeVariation(Base, TimestampMixin):
    """Tracks specific variations within a recipe cluster."""

    __tablename__ = "recipe_variations"

    id: int = Column(Integer, primary_key=True)
    cluster_id: int = Column(Integer, ForeignKey("recipe_clusters.id"))
    name: str = Column(String(200))
    description: Optional[str] = Column(Text)
    modifications: Dict[str, Any] = Column(JSONB)
    impact_areas: List[ModificationImpact] = Column(JSONB)
    success_rate: Optional[float] = Column(Float)
    popularity_score: Optional[float] = Column(Float)
    target_skill_level: Optional[int] = Column(Integer)
    equipment_requirements: List[str] = Column(JSONB)
    cost_impact: Optional[float] = Column(Float)
    time_impact: Optional[int] = Column(Integer)

    # Relationships
    cluster: Mapped["RecipeCluster"] = relationship(
        "RecipeCluster", back_populates="variations"
    )
    modifications_tracking: Mapped[List["RecipeModificationTracking"]] = relationship(
        "RecipeModificationTracking", back_populates="variation"
    )


class RecipeModificationTracking(Base, TimestampMixin):
    """Tracks individual recipe modifications and their outcomes."""

    __tablename__ = "recipe_modification_tracking"

    id: int = Column(Integer, primary_key=True)
    variation_id: int = Column(Integer, ForeignKey("recipe_variations.id"))
    recipe_id: int = Column(Integer, ForeignKey("recipes.id"))
    user_id: int = Column(Integer, ForeignKey("users.id"))
    modification_type: str = Column(String(50))
    original_value: Dict[str, Any] = Column(JSONB)
    modified_value: Dict[str, Any] = Column(JSONB)
    reason: Optional[str] = Column(Text)
    impact_areas: List[ModificationImpact] = Column(JSONB)
    impact_scores: Dict[str, float] = Column(JSONB)
    user_skill_level: Optional[int] = Column(Integer)
    user_preferences: Dict[str, Any] = Column(JSONB)
    cooking_context: Dict[str, Any] = Column(JSONB)
    success_rating: Optional[float] = Column(Float)
    would_recommend: Optional[bool] = Column(Boolean)
    notes: Optional[str] = Column(Text)

    # Relationships
    variation: Mapped["RecipeVariation"] = relationship(
        "RecipeVariation", back_populates="modifications_tracking"
    )
    recipe: Mapped["Recipe"] = relationship("Recipe")
    user: Mapped["User"] = relationship("User")


class RecipeTrend(Base, TimestampMixin):
    """Tracks recipe popularity and trends over time."""

    __tablename__ = "recipe_trends"

    id: int = Column(Integer, primary_key=True)
    recipe_id: int = Column(Integer, ForeignKey("recipes.id"))
    cluster_id: int = Column(Integer, ForeignKey("recipe_clusters.id"))
    variation_id: Optional[int] = Column(Integer, ForeignKey("recipe_variations.id"))
    period_start: datetime = Column(DateTime)
    period_end: datetime = Column(DateTime)
    view_count: int = Column(Integer, default=0)
    save_count: int = Column(Integer, default=0)
    cook_count: int = Column(Integer, default=0)
    review_count: int = Column(Integer, default=0)
    avg_rating: Optional[float] = Column(Float)
    comment_count: int = Column(Integer, default=0)
    share_count: int = Column(Integer, default=0)
    modification_count: int = Column(Integer, default=0)
    momentum_score: Optional[float] = Column(Float)
    virality_score: Optional[float] = Column(Float)
    value_score: Optional[float] = Column(Float)
    seasonal_factor: Optional[float] = Column(Float)
    regional_popularity: Dict[str, float] = Column(JSONB)
    demographic_breakdown: Dict[str, Any] = Column(JSONB)
    overall_rank: Optional[int] = Column(Integer)
    category_rank: Optional[int] = Column(Integer)
    value_rank: Optional[int] = Column(Integer)

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe")
    cluster: Mapped["RecipeCluster"] = relationship("RecipeCluster")
    variation: Mapped[Optional["RecipeVariation"]] = relationship("RecipeVariation")
