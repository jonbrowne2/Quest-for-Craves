"""User analysis service for recipe value system."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from recipe_value_system.models.user_interactions import (
    UserCookingHistory,
    UserPreferences,
    UserRecipeInteraction,
)
from recipe_value_system.services.core.base_service import BaseService


@dataclass
class UserStats:
    """User activity statistics."""

    total_interactions: int
    recipes_cooked: int
    has_preferences: bool
    last_active: str


@dataclass
class CookingTrend:
    """User cooking trend information."""

    recipe_id: int
    cooked_at: str
    success_level: Optional[str]
    had_modifications: bool


class UserAnalysisService(BaseService):
    """Service for analyzing user behavior and preferences."""

    def __init__(self, session: Session) -> None:
        """Initialize service with database session."""
        super().__init__()
        self.session = session
        self._initialized = True

    def get_user_stats(self, user_id: int) -> UserStats:
        """Get statistics for a user."""
        interactions = (
            self.session.query(UserRecipeInteraction)
            .filter(UserRecipeInteraction.user_id == user_id)
            .all()
        )
        cooking_history = (
            self.session.query(UserCookingHistory)
            .filter(UserCookingHistory.user_id == user_id)
            .all()
        )
        preferences = (
            self.session.query(UserPreferences)
            .filter(UserPreferences.user_id == user_id)
            .first()
        )

        last_active = max(
            (i.created_at for i in interactions),
            default=datetime.min,
        )

        return UserStats(
            total_interactions=len(interactions),
            recipes_cooked=len(cooking_history),
            has_preferences=preferences is not None,
            last_active=last_active.isoformat(),
        )

    def get_cooking_trends(self, user_id: int) -> List[CookingTrend]:
        """Get cooking trends for a user."""
        history = (
            self.session.query(UserCookingHistory)
            .filter(UserCookingHistory.user_id == user_id)
            .order_by(UserCookingHistory.cooked_at.desc())
            .all()
        )

        return [
            CookingTrend(
                recipe_id=h.recipe_id,
                cooked_at=h.cooked_at.isoformat(),
                success_level=h.success_level.value if h.success_level else None,
                had_modifications=bool(h.modifications),
            )
            for h in history
        ]
