"""User interactions and preferences service."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set

from ..models.recipe import Recipe
from ..models.user_interactions import CookingHistory, UserPreference
from .core.base_service import BaseService, ServiceStatus


@dataclass
class InteractionStats:
    """User interaction statistics."""

    total_recipes_cooked: int = 0
    favorite_cuisines: Set[str] = field(default_factory=set)
    average_cooking_time: Optional[int] = None
    last_active: datetime = field(default_factory=datetime.utcnow)
    completed_difficulty_levels: Set[str] = field(default_factory=set)


@dataclass
class PreferenceUpdate:
    """User preference update request."""

    user_id: int
    preference_type: str  # cuisine, diet, difficulty
    value: str
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CookingEvent:
    """Cooking event record."""

    user_id: int
    recipe_id: int
    cooking_time: Optional[int] = None
    completed: bool = False
    notes: Optional[str] = None
    cooked_at: datetime = field(default_factory=datetime.utcnow)


class UserInteractionService(BaseService):
    """Service for managing user interactions and preferences."""

    def __init__(self) -> None:
        """Initialize the user interaction service."""
        super().__init__()
        self._user_stats: dict[int, InteractionStats] = {}
        self._user_preferences: dict[int, List[UserPreference]] = {}
        self._cooking_history: dict[int, List[CookingHistory]] = {}

    def initialize(self) -> bool:
        """Initialize service and load required data."""
        try:
            # Load existing user data
            self._load_user_data()
            self._status = ServiceStatus(is_ready=True)
            return True
        except Exception as e:
            self._status = ServiceStatus(
                is_ready=False,
                error=f"Failed to initialize user interaction service: {str(e)}",
            )
            return False

    def get_user_stats(self, user_id: int) -> Optional[InteractionStats]:
        """Get user interaction statistics."""
        return self._user_stats.get(user_id)

    def get_user_preferences(self, user_id: int) -> List[UserPreference]:
        """Get user preferences."""
        return self._user_preferences.get(user_id, [])

    def get_cooking_history(self, user_id: int) -> List[CookingHistory]:
        """Get user cooking history."""
        return self._cooking_history.get(user_id, [])

    def update_preference(self, update: PreferenceUpdate) -> bool:
        """Update user preference."""
        if not self._status.is_ready:
            return False

        try:
            preference = UserPreference(
                user_id=update.user_id,
                preference_type=update.preference_type,
                value=update.value,
                updated_at=update.updated_at,
            )

            # Update or add preference
            if update.user_id not in self._user_preferences:
                self._user_preferences[update.user_id] = []

            prefs = self._user_preferences[update.user_id]

            # Remove existing preference of same type if exists
            prefs = [p for p in prefs if p.preference_type != update.preference_type]
            prefs.append(preference)
            self._user_preferences[update.user_id] = prefs

            # Update stats
            if update.preference_type == "cuisine":
                stats = self._get_or_create_stats(update.user_id)
                stats.favorite_cuisines.add(update.value)

            return True
        except Exception as e:
            self._status = ServiceStatus(
                is_ready=True, error=f"Failed to update preference: {str(e)}"
            )
            return False

    def record_cooking_event(self, event: CookingEvent) -> bool:
        """Record a cooking event."""
        if not self._status.is_ready:
            return False

        try:
            history = CookingHistory(
                user_id=event.user_id,
                recipe_id=event.recipe_id,
                cooking_time=event.cooking_time,
                completed=event.completed,
                notes=event.notes,
                cooked_at=event.cooked_at,
            )

            # Add to history
            if event.user_id not in self._cooking_history:
                self._cooking_history[event.user_id] = []
            self._cooking_history[event.user_id].append(history)

            # Update stats
            stats = self._get_or_create_stats(event.user_id)
            if event.completed:
                stats.total_recipes_cooked += 1

                # Update average cooking time
                if event.cooking_time:
                    if stats.average_cooking_time is None:
                        stats.average_cooking_time = event.cooking_time
                    else:
                        stats.average_cooking_time = (
                            stats.average_cooking_time + event.cooking_time
                        ) // 2

                # Update last active time
                if event.cooked_at > stats.last_active:
                    stats.last_active = event.cooked_at

                # Update completed difficulty levels
                recipe = self._get_recipe(event.recipe_id)
                if recipe and recipe.difficulty_level:
                    stats.completed_difficulty_levels.add(recipe.difficulty_level)

            return True
        except Exception as e:
            self._status = ServiceStatus(
                is_ready=True, error=f"Failed to record cooking event: {str(e)}"
            )
            return False

    def _get_or_create_stats(self, user_id: int) -> InteractionStats:
        """Get or create user statistics."""
        if user_id not in self._user_stats:
            self._user_stats[user_id] = InteractionStats()
        return self._user_stats[user_id]

    def _load_user_data(self) -> None:
        """Load user data from database."""
        # TODO: Implement data loading from database
        pass

    def _get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by ID."""
        # TODO: Implement recipe loading from database
        return None
