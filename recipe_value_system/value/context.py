"""
Context management for recipe value calculations.

This module provides tools for building and managing context information
that influences recipe value calculations.
"""

import datetime
from typing import Any, Dict, List, Optional

try:
    from ..config import SystemConfig
except ImportError:
    # For direct module usage
    try:
        from recipe_value_system.config import SystemConfig
    except ImportError:
        # Fallback for testing
        SystemConfig = object  # type: ignore


class ContextManager:
    """Manager for building and enriching context for value calculations.

    Provides tools for gathering user context, environmental factors, and
    other contextual information that may influence recipe value.
    """

    def __init__(self, session: Any) -> None:
        """Initialize the context manager.

        Args:
            session: Database session
        """
        self.session = session
        self.default_context: Dict[str, Any] = {
            "time_of_day": "any",
            "day_of_week": "any",
            "season": "any",
            "weather": "any",
            "occasion": "everyday",
        }

    def get_context(
        self, user_id: int, provided_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build complete context including user state and preferences.

        Args:
            user_id: User ID
            provided_context: Optional context provided by caller

        Returns:
            Complete context dictionary
        """
        base_context = self._get_base_context(user_id)
        if provided_context:
            base_context.update(provided_context)

        return self._enrich_context(base_context)

    def _get_base_context(self, user_id: int) -> Dict[str, Any]:
        """Get base context from user data.

        Args:
            user_id: User ID

        Returns:
            Base context dictionary
        """
        return {
            "time_of_day": self._get_current_time_context(),
            "user_preferences": self._get_user_preferences(user_id),
            "dietary_restrictions": self._get_dietary_restrictions(user_id),
            "skill_level": self._get_user_skill_level(user_id),
        }

    def _enrich_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with additional information.

        Args:
            context: Base context

        Returns:
            Enriched context
        """
        enriched = context.copy()

        # Add seasonal information if not provided
        if "season" not in enriched:
            enriched["season"] = self._get_current_season()

        # Add day of week if not provided
        if "day_of_week" not in enriched:
            enriched["day_of_week"] = self._get_current_day_of_week()

        # Add weather information if not provided and available
        if "weather" not in enriched:
            enriched["weather"] = self._get_weather_context()

        return enriched

    def _get_current_time_context(self) -> str:
        """Get time of day context.

        Returns:
            Time of day category
        """
        now = datetime.datetime.now()
        hour = now.hour

        if 5 <= hour < 11:
            return "morning"
        elif 11 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "dinner"
        else:
            return "late_night"

    def _get_current_season(self) -> str:
        """Get current season.

        Returns:
            Current season
        """
        now = datetime.datetime.now()
        month = now.month

        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "fall"
        else:
            return "winter"

    def _get_current_day_of_week(self) -> str:
        """Get current day of week.

        Returns:
            Day of week
        """
        now = datetime.datetime.now()
        weekday = now.weekday()

        if weekday < 5:
            return "weekday"
        else:
            return "weekend"

    def _get_weather_context(self) -> str:
        """Get weather context.

        Returns:
            Weather category or 'unknown' if not available
        """
        # Implementation would get weather data from external service
        return "unknown"

    def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences.

        Args:
            user_id: User ID

        Returns:
            User preferences
        """
        # Implementation would retrieve from database
        return {
            "preferred_cuisines": ["italian", "mexican"],
            "preferred_flavors": ["savory", "spicy"],
            "disliked_ingredients": ["cilantro", "olives"],
        }

    def _get_dietary_restrictions(self, user_id: int) -> List[str]:
        """Get user dietary restrictions.

        Args:
            user_id: User ID

        Returns:
            List of dietary restrictions
        """
        # Implementation would retrieve from database
        return ["gluten-free"]

    def _get_user_skill_level(self, user_id: int) -> str:
        """Get user cooking skill level.

        Args:
            user_id: User ID

        Returns:
            Skill level
        """
        # Implementation would retrieve from database
        return "intermediate"
