"""Recipe recommendation service."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set

from ...analytics.business_insights import RecipeMetrics
from ...models.recipe import Recipe
from ...models.user_interactions import CookingHistory, UserPreference
from ..core.base_service import BaseService, ServiceStatus


@dataclass
class UserProfile:
    """User cooking preferences and history."""

    user_id: int
    favorite_cuisines: Set[str] = field(default_factory=set)
    dietary_restrictions: Set[str] = field(default_factory=set)
    preferred_difficulty: Optional[str] = None
    avg_cooking_time: Optional[int] = None
    last_active: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RecommendationScore:
    """Recipe recommendation scoring."""

    recipe_id: int
    base_score: float = 0.0
    quality_score: float = 0.0
    preference_score: float = 0.0
    novelty_score: float = 0.0
    seasonal_score: float = 0.0
    final_score: float = 0.0


@dataclass
class RecommendationRequest:
    """Recipe recommendation request parameters."""

    user_id: int
    count: int = 5
    cuisine_type: Optional[str] = None
    max_cooking_time: Optional[int] = None
    difficulty_level: Optional[str] = None
    dietary_restrictions: Set[str] = field(default_factory=set)


@dataclass
class RecommendationResult:
    """Recipe recommendation result."""

    recipe: Recipe
    score: RecommendationScore
    reason: str


class RecipeRecommender(BaseService):
    """Service for generating personalized recipe recommendations."""

    def __init__(self) -> None:
        """Initialize the recipe recommender service."""
        super().__init__()
        self._user_profiles: dict[int, UserProfile] = {}
        self._recipe_metrics: dict[int, RecipeMetrics] = {}

    def initialize(self) -> bool:
        """Initialize service and load required data."""
        try:
            # Load user preferences and history
            self._load_user_profiles()
            # Load recipe metrics
            self._load_recipe_metrics()
            self._status = ServiceStatus(is_ready=True)
            return True
        except Exception as e:
            self._status = ServiceStatus(
                is_ready=False,
                error=f"Failed to initialize recipe recommender: {str(e)}",
            )
            return False

    def get_recommendations(
        self, request: RecommendationRequest
    ) -> List[RecommendationResult]:
        """Get personalized recipe recommendations."""
        if not self._status.is_ready:
            return []

        # Get user profile
        profile = self._get_or_create_profile(request.user_id)

        # Update profile with request preferences
        if request.cuisine_type:
            profile.favorite_cuisines.add(request.cuisine_type)
        if request.dietary_restrictions:
            profile.dietary_restrictions.update(request.dietary_restrictions)
        if request.difficulty_level:
            profile.preferred_difficulty = request.difficulty_level

        # Score all recipes
        scored_recipes = []
        for recipe_id, metrics in self._recipe_metrics.items():
            score = self._calculate_recommendation_score(
                recipe_id, metrics, profile, request
            )
            if score.final_score > 0:
                recipe = self._get_recipe(recipe_id)
                if recipe:
                    reason = self._generate_recommendation_reason(
                        score, recipe, profile
                    )
                    scored_recipes.append(
                        RecommendationResult(recipe=recipe, score=score, reason=reason)
                    )

        # Sort by final score and return top N
        scored_recipes.sort(key=lambda x: x.score.final_score, reverse=True)
        return scored_recipes[: request.count]

    def update_user_preferences(
        self, user_id: int, preferences: List[UserPreference]
    ) -> None:
        """Update user preferences in profile."""
        profile = self._get_or_create_profile(user_id)

        for pref in preferences:
            if pref.preference_type == "cuisine":
                profile.favorite_cuisines.add(pref.value)
            elif pref.preference_type == "diet":
                profile.dietary_restrictions.add(pref.value)
            elif pref.preference_type == "difficulty":
                profile.preferred_difficulty = pref.value

        profile.last_active = datetime.utcnow()

    def update_cooking_history(
        self, user_id: int, history: List[CookingHistory]
    ) -> None:
        """Update user cooking history in profile."""
        profile = self._get_or_create_profile(user_id)

        if history:
            # Calculate average cooking time
            times = [h.cooking_time for h in history if h.cooking_time]
            if times:
                profile.avg_cooking_time = sum(times) / len(times)

            # Update last active
            latest = max(h.cooked_at for h in history)
            if latest > profile.last_active:
                profile.last_active = latest

    def _get_or_create_profile(self, user_id: int) -> UserProfile:
        """Get existing user profile or create new one."""
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = UserProfile(user_id=user_id)
        return self._user_profiles[user_id]

    def _calculate_recommendation_score(
        self,
        recipe_id: int,
        metrics: RecipeMetrics,
        profile: UserProfile,
        request: RecommendationRequest,
    ) -> RecommendationScore:
        """Calculate recommendation score for a recipe."""
        score = RecommendationScore(recipe_id=recipe_id)
        recipe = self._get_recipe(recipe_id)

        if not recipe:
            return score

        # Base score from recipe quality
        score.quality_score = metrics.overall_quality
        score.base_score = score.quality_score

        # Preference score
        if recipe.cuisine_type in profile.favorite_cuisines:
            score.preference_score += 0.3
        if recipe.difficulty_level == profile.preferred_difficulty:
            score.preference_score += 0.2
        if profile.avg_cooking_time:
            if recipe.total_time and recipe.total_time <= profile.avg_cooking_time:
                score.preference_score += 0.2

        # Check dietary restrictions
        if profile.dietary_restrictions:
            if not recipe.diet_categories:
                return score  # Zero score if no diet info
            if not profile.dietary_restrictions.issubset(set(recipe.diet_categories)):
                return score  # Zero score if restrictions not met

        # Novelty score (favor recipes not recently cooked)
        score.novelty_score = 0.3  # Default novelty

        # Seasonal score (based on current season)
        score.seasonal_score = 0.2  # Default seasonal relevance

        # Calculate final weighted score
        score.final_score = (
            0.4 * score.base_score
            + 0.3 * score.preference_score
            + 0.2 * score.novelty_score
            + 0.1 * score.seasonal_score
        )

        return score

    def _generate_recommendation_reason(
        self, score: RecommendationScore, recipe: Recipe, profile: UserProfile
    ) -> str:
        """Generate human-readable recommendation reason."""
        reasons = []

        if score.quality_score >= 0.8:
            reasons.append("high-quality recipe")
        if recipe.cuisine_type in profile.favorite_cuisines:
            reasons.append(f"matches your preferred {recipe.cuisine_type} cuisine")
        if recipe.difficulty_level == profile.preferred_difficulty:
            reasons.append(f"matches your {recipe.difficulty_level} skill level")
        if score.novelty_score >= 0.3:
            reasons.append("something new to try")
        if score.seasonal_score >= 0.2:
            reasons.append("perfect for this season")

        if not reasons:
            return "Recommended based on your preferences"

        return "Recommended because: " + ", ".join(reasons)

    def _load_user_profiles(self) -> None:
        """Load user profiles from database."""
        # TODO: Implement profile loading from database
        pass

    def _load_recipe_metrics(self) -> None:
        """Load recipe quality metrics."""
        # TODO: Implement metrics loading from database
        pass

    def _get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by ID."""
        # TODO: Implement recipe loading from database
        return None
