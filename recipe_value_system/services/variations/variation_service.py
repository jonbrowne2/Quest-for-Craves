"""Service for managing recipe variations and trends."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recipe_value_system.config.config import SystemConfig
from recipe_value_system.models.recipe import Recipe
from recipe_value_system.models.recipe_variations import (
    RecipeCluster,
    RecipeClusterType,
    RecipeModificationTracking,
    RecipeTrend,
    RecipeVariation,
)


class VariationService:
    """Service for managing recipe variations and trends."""

    def __init__(self, session, config: SystemConfig) -> None:
        """Initialize the VariationService.

        Args:
            session: Database session.
            config: System configuration.
        """
        self.session = session
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize text vectorizer
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))

    def find_similar_recipes(
        self, recipe: Recipe, threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Find similar recipes using ingredient and instruction similarity.

        Args:
            recipe: Recipe to find similar recipes for.
            threshold: Similarity threshold. Defaults to 0.8.

        Returns:
            List of similar recipes with similarity score and relationship type.
        """
        # Get all recipes
        all_recipes = self.session.query(Recipe).all()

        # Prepare text for comparison
        recipe_texts = []
        for r in all_recipes:
            # Combine ingredients and instructions
            ingredients = " ".join([i["name"] for i in r.ingredients])
            instructions = " ".join([i["text"] for i in r.instructions])
            recipe_texts.append(f"{ingredients} {instructions}")

        # Calculate similarity matrix
        matrix = self.vectorizer.fit_transform(recipe_texts)
        similarities = cosine_similarity(matrix)

        # Find similar recipes
        similar_recipes = []
        for i, score in enumerate(similarities[recipe.id]):
            if score >= threshold and i != recipe.id:
                relationship = self._determine_relationship_type(score)
                similar_recipes.append(
                    {
                        "recipe": all_recipes[i],
                        "similarity": float(score),
                        "relationship": relationship,
                    }
                )

        return sorted(similar_recipes, key=lambda x: x["similarity"], reverse=True)

    def _determine_relationship_type(
        self, similarity_score: float
    ) -> RecipeClusterType:
        """Determine relationship type based on similarity score.

        Args:
            similarity_score: Similarity score.

        Returns:
            RecipeClusterType: Relationship type.
        """
        if similarity_score >= 0.9:
            return RecipeClusterType.IDENTICAL
        elif similarity_score >= 0.8:
            return RecipeClusterType.SIMILAR
        elif similarity_score >= 0.6:
            return RecipeClusterType.VARIANT
        else:
            return RecipeClusterType.INSPIRED

    def create_or_update_cluster(self, recipe: Recipe) -> RecipeCluster:
        """Create or update a recipe cluster.

        Args:
            recipe: Recipe to create or update cluster for.

        Returns:
            RecipeCluster: Created or updated cluster.
        """
        # Find similar recipes
        similar_recipes = self.find_similar_recipes(recipe)

        # Check if recipe belongs to existing cluster
        existing_cluster = None
        for similar in similar_recipes:
            if similar["similarity"] >= 0.8:  # High similarity threshold
                clusters = similar["recipe"].clusters
                if clusters:
                    existing_cluster = clusters[0]
                    break

        if existing_cluster:
            # Add recipe to existing cluster
            existing_cluster.recipes.append(recipe)
            self._update_cluster_metrics(existing_cluster)
            return existing_cluster

        # Create new cluster
        cluster = RecipeCluster(
            name=recipe.title,
            description=f"Variations of {recipe.title}",
            core_ingredients=self._extract_core_ingredients([recipe]),
            optional_ingredients=self._extract_optional_ingredients([recipe]),
            key_techniques=self._extract_key_techniques([recipe]),
        )

        cluster.recipes.append(recipe)
        self.session.add(cluster)
        self._update_cluster_metrics(cluster)

        return cluster

    def track_modification(
        self, recipe: Recipe, user_id: int, modifications: Dict[str, Any]
    ) -> RecipeModificationTracking:
        """Track a recipe modification.

        Args:
            recipe: Recipe to track modification for.
            user_id: User ID.
            modifications: Modification details.

        Returns:
            RecipeModificationTracking: Tracked modification.
        """
        # Find or create variation
        variation = self._get_or_create_variation(recipe)

        # Create modification tracking
        tracking = RecipeModificationTracking(
            variation_id=variation.id,
            recipe_id=recipe.id,
            user_id=user_id,
            modification_type=modifications.get("type"),
            original_value=modifications.get("original"),
            modified_value=modifications.get("modified"),
            reason=modifications.get("reason"),
            impact_areas=modifications.get("impact_areas"),
            user_skill_level=modifications.get("user_skill_level"),
            user_preferences=modifications.get("preferences"),
            cooking_context=modifications.get("context"),
        )

        self.session.add(tracking)
        return tracking

    def update_trends(self, period_days: int = 7) -> List[RecipeTrend]:
        """Update recipe trends for the specified period.

        Args:
            period_days: Period in days. Defaults to 7.

        Returns:
            List of updated trends.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        # Get all recipes
        recipes = self.session.query(Recipe).all()
        trends = []

        for recipe in recipes:
            # Calculate trend metrics
            trend = self._calculate_recipe_trend(recipe, start_date, end_date)
            trends.append(trend)

        # Calculate rankings
        self._update_trend_rankings(trends)

        self.session.add_all(trends)
        return trends

    def get_trending_recipes(
        self, category: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get trending recipes, optionally filtered by category.

        Args:
            category: Category filter. Defaults to None.
            limit: Result limit. Defaults to 100.

        Returns:
            List of trending recipes with rank and metrics.
        """
        query = self.session.query(RecipeTrend)

        if category:
            query = query.join(Recipe).filter(Recipe.category == category)

        trends = query.order_by(RecipeTrend.momentum_score).limit(limit).all()

        return [
            {
                "recipe": trend.recipe,
                "rank": trend.overall_rank,
                "momentum": trend.momentum_score,
                "value_score": trend.value_score,
                "review_count": trend.review_count,
                "avg_rating": trend.avg_rating,
            }
            for trend in trends
        ]

    def _extract_core_ingredients(self, recipes: List[Recipe]) -> List[Dict]:
        """Extract core ingredients common across recipe variations.

        Args:
            recipes: Recipes to extract core ingredients from.

        Returns:
            List of core ingredients.
        """
        # Implementation would identify common essential ingredients
        pass

    def _extract_optional_ingredients(self, recipes: List[Recipe]) -> List[Dict]:
        """Extract optional ingredients across recipe variations.

        Args:
            recipes: Recipes to extract optional ingredients from.

        Returns:
            List of optional ingredients.
        """
        # Implementation would identify ingredients that vary
        pass

    def _extract_key_techniques(self, recipes: List[Recipe]) -> List[str]:
        """Extract key techniques used across recipe variations.

        Args:
            recipes: Recipes to extract key techniques from.

        Returns:
            List of key techniques.
        """
        # Implementation would identify common cooking techniques
        pass

    def _update_cluster_metrics(self, cluster: RecipeCluster) -> None:
        """Update aggregate metrics for a recipe cluster.

        Args:
            cluster: Cluster to update metrics for.
        """
        recipes = cluster.recipes

        cluster.avg_rating = np.mean([r.community_rating for r in recipes])
        cluster.total_reviews = sum(r.review_count for r in recipes)
        cluster.popularity_score = self._calculate_popularity_score(recipes)

    def _calculate_popularity_score(self, recipes: List[Recipe]) -> float:
        """Calculate popularity score for a group of recipes.

        Args:
            recipes: Recipes to calculate popularity score for.

        Returns:
            Popularity score.
        """
        # Implementation would consider various engagement metrics
        pass

    def _get_or_create_variation(self, recipe: Recipe) -> RecipeVariation:
        """Get or create a variation record for a recipe.

        Args:
            recipe: Recipe to get or create variation for.

        Returns:
            RecipeVariation: Variation record.
        """
        variation = (
            self.session.query(RecipeVariation)
            .filter_by(base_recipe_id=recipe.id)
            .first()
        )

        if not variation:
            cluster = self.create_or_update_cluster(recipe)
            variation = RecipeVariation(
                cluster_id=cluster.id,
                base_recipe_id=recipe.id,
                name=recipe.title,
                description=f"Variations of {recipe.title}",
            )
            self.session.add(variation)

        return variation

    def _calculate_recipe_trend(
        self, recipe: Recipe, start_date: datetime, end_date: datetime
    ) -> RecipeTrend:
        """Calculate trend metrics for a recipe.

        Args:
            recipe: Recipe to calculate trend for.
            start_date: Start date of the period.
            end_date: End date of the period.

        Returns:
            RecipeTrend: Trend metrics.
        """
        # Get previous trend for momentum calculation
        prev_start = start_date - timedelta(days=(end_date - start_date).days)
        prev_trend = (
            self.session.query(RecipeTrend)
            .filter_by(recipe_id=recipe.id)
            .filter(RecipeTrend.period_start == prev_start)
            .first()
        )

        # Calculate current metrics
        current_metrics = self._get_period_metrics(recipe, start_date, end_date)

        # Calculate momentum (growth rate)
        momentum = 0.0
        if prev_trend:
            momentum = current_metrics[
                "engagement_score"
            ] - self._calculate_engagement_score(prev_trend)

        return RecipeTrend(
            recipe_id=recipe.id,
            cluster_id=recipe.clusters[0].id if recipe.clusters else None,
            period_start=start_date,
            period_end=end_date,
            **current_metrics,
            momentum_score=momentum,
        )

    def _get_period_metrics(
        self, recipe: Recipe, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get recipe metrics for a specific period.

        Args:
            recipe: Recipe to get metrics for.
            start_date: Start date of the period.
            end_date: End date of the period.

        Returns:
            Metrics for the period.
        """
        # Implementation would calculate various engagement metrics
        pass

    def _calculate_engagement_score(self, trend: RecipeTrend) -> float:
        """Calculate overall engagement score from trend metrics.

        Args:
            trend: Trend metrics.

        Returns:
            Engagement score.
        """
        # Implementation would combine various metrics into a score
        pass

    def _update_trend_rankings(self, trends: List[RecipeTrend]) -> None:
        """Update rankings for all trends.

        Args:
            trends: Trends to update rankings for.
        """
        # Sort by different metrics and update ranks
        by_momentum = sorted(trends, key=lambda x: x.momentum_score, reverse=True)
        by_value = sorted(trends, key=lambda x: x.value_score, reverse=True)

        # Update overall ranks
        for i, trend in enumerate(by_momentum):
            trend.overall_rank = i + 1

        # Update value ranks
        for i, trend in enumerate(by_value):
            trend.value_rank = i + 1
