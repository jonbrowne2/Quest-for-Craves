"""API endpoints for recipe variations and trends."""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from recipe_value_system.config import SystemConfig
from recipe_value_system.models.recipe_variations import (
    ModificationImpact,
    RecipeClusterType,
)
from recipe_value_system.services.variations.variation_service import VariationService

router = APIRouter(prefix="/api/v1/trends")


class TimePeriod(str, Enum):
    """
    Time periods for rankings.

    TODAY: Today
    WEEK: Week
    MONTH: Month
    YEAR: Year
    ALL_TIME: All time
    """

    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL_TIME = "all_time"


class RankingType(str, Enum):
    """
    Types of rankings.

    OVERALL: Overall ranking
    VALUE: Value ranking
    TASTE: Taste ranking
    """

    OVERALL = "overall"
    VALUE = "value"
    TASTE = "taste"


# Pydantic models
class RecipeRank(BaseModel):
    """
    Model for recipe ranking data.

    Attributes:
        recipe_id (int): Recipe ID
        title (str): Recipe title
        rank (int): Recipe rank
        previous_rank (Optional[int]): Previous recipe rank
        momentum_score (float): Momentum score
        value_score (float): Value score
        taste_score (float): Taste score
        review_count (int): Review count
        avg_rating (float): Average rating
        photo_url (Optional[str]): Photo URL
        cuisine_type (str): Cuisine type
        difficulty_score (float): Difficulty score
        prep_time (int): Prep time
        total_time (int): Total time
        cost_per_serving (float): Cost per serving
        calories_per_serving (int): Calories per serving
    """

    recipe_id: int
    title: str
    rank: int
    previous_rank: Optional[int]
    momentum_score: float
    value_score: float
    taste_score: float
    review_count: int
    avg_rating: float
    photo_url: Optional[str]
    cuisine_type: str
    difficulty_score: float
    prep_time: int
    total_time: int
    cost_per_serving: float
    calories_per_serving: int


class TrendingRecipes(BaseModel):
    """
    Model for trending recipes response.

    Attributes:
        period_start (datetime): Period start date
        period_end (datetime): Period end date
        rankings (List[RecipeRank]): Recipe rankings
        category_stats (dict): Category statistics
        trending_ingredients (List[dict]): Trending ingredients
        trending_modifications (List[dict]): Trending modifications
    """

    period_start: datetime
    period_end: datetime
    rankings: List[RecipeRank]
    category_stats: dict
    trending_ingredients: List[dict]
    trending_modifications: List[dict]


class ModificationStats(BaseModel):
    """
    Model for modification statistics.

    Attributes:
        modification_type (str): Modification type
        success_rate (float): Success rate
        avg_impact (dict): Average impact
        popular_with (List[str]): Popular with
        example_recipes (List[int]): Example recipes
    """

    modification_type: str
    success_rate: float
    avg_impact: dict
    popular_with: List[str]
    example_recipes: List[int]


# API endpoints
@router.get("/hot100", response_model=TrendingRecipes)
async def get_hot_100(
    ranking_type: RankingType = Query(
        RankingType.OVERALL, description="Type of ranking"
    ),
    time_period: TimePeriod = Query(
        TimePeriod.WEEK, description="Time period for rankings"
    ),
    category: Optional[str] = None,
    cuisine: Optional[str] = None,
    session=Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Get the Hot 100 recipes for the specified time period.

    Args:
        ranking_type (RankingType): Type of ranking
        time_period (TimePeriod): Time period for rankings
        category (Optional[str]): Category
        cuisine (Optional[str]): Cuisine
        session: Database session
        config (SystemConfig): System configuration

    Returns:
        TrendingRecipes: Trending recipes response
    """
    service = VariationService(session, config)

    try:
        # Calculate date range based on time period
        end_date = datetime.utcnow()
        if time_period == TimePeriod.TODAY:
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == TimePeriod.WEEK:
            start_date = end_date - timedelta(days=7)
        elif time_period == TimePeriod.MONTH:
            start_date = end_date - timedelta(days=30)
        elif time_period == TimePeriod.YEAR:
            start_date = end_date - timedelta(days=365)
        else:  # ALL_TIME
            start_date = None

        # Get trending recipes
        trending = service.get_trending_recipes(
            start_date=start_date,
            end_date=end_date,
            ranking_type=ranking_type,
            category=category,
            cuisine=cuisine,
            limit=100,
        )

        # Format response
        rankings = []
        for rank, trend in enumerate(trending, 1):
            recipe = trend["recipe"]
            rankings.append(
                {
                    "recipe_id": recipe.id,
                    "title": recipe.title,
                    "rank": rank,
                    "previous_rank": trend.get("previous_rank"),
                    "momentum_score": trend["momentum"],
                    "value_score": trend["value_score"],
                    "taste_score": recipe.taste_score,
                    "review_count": trend["review_count"],
                    "avg_rating": trend["avg_rating"],
                    "photo_url": recipe.photo_url,
                    "cuisine_type": recipe.cuisine_type,
                    "difficulty_score": recipe.difficulty_score,
                    "prep_time": recipe.prep_time,
                    "total_time": recipe.total_time,
                    "cost_per_serving": float(recipe.cost_per_serving),
                    "calories_per_serving": recipe.calories_per_serving,
                }
            )

        # Get category statistics and trends
        category_stats = service.get_category_stats(
            rankings, start_date=start_date, end_date=end_date
        )

        trending_ingredients = service.get_trending_ingredients(
            start_date=start_date, end_date=end_date
        )

        trending_modifications = service.get_trending_modifications(
            start_date=start_date, end_date=end_date
        )

        period_start = start_date or service.get_first_recipe_date()

        return {
            "period_start": period_start,
            "period_end": end_date,
            "rankings": rankings,
            "category_stats": category_stats,
            "trending_ingredients": trending_ingredients,
            "trending_modifications": trending_modifications,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories")
async def get_trending_categories(
    session=Depends(get_db), config: SystemConfig = Depends(get_config)
):
    """
    Get trending recipe categories.

    Args:
        session: Database session
        config (SystemConfig): System configuration

    Returns:
        List[str]: Trending categories
    """
    service = VariationService(session, config)
    return service.get_trending_categories()


@router.get("/modifications", response_model=List[ModificationStats])
async def get_trending_modifications(
    recipe_id: Optional[int] = None,
    category: Optional[str] = None,
    impact_area: Optional[ModificationImpact] = None,
    session=Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Get trending recipe modifications.

    Args:
        recipe_id (Optional[int]): Recipe ID
        category (Optional[str]): Category
        impact_area (Optional[ModificationImpact]): Impact area
        session: Database session
        config (SystemConfig): System configuration

    Returns:
        List[ModificationStats]: Trending modifications
    """
    service = VariationService(session, config)
    return service.get_trending_modifications(
        recipe_id=recipe_id, category=category, impact_area=impact_area
    )


@router.get("/similar/{recipe_id}")
async def get_similar_recipes(
    recipe_id: int,
    threshold: float = Query(0.8, ge=0.0, le=1.0),
    session=Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Get similar recipes for a given recipe.

    Args:
        recipe_id (int): Recipe ID
        threshold (float): Similarity threshold
        session: Database session
        config (SystemConfig): System configuration

    Returns:
        List[Recipe]: Similar recipes
    """
    service = VariationService(session, config)
    recipe = service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return service.find_similar_recipes(recipe, threshold)


@router.get("/variations/{recipe_id}")
async def get_recipe_variations(
    recipe_id: int, session=Depends(get_db), config: SystemConfig = Depends(get_config)
):
    """
    Get all variations of a recipe.

    Args:
        recipe_id (int): Recipe ID
        session: Database session
        config (SystemConfig): System configuration

    Returns:
        List[Recipe]: Recipe variations
    """
    service = VariationService(session, config)
    return service.get_recipe_variations(recipe_id)


@router.get("/history/{recipe_id}")
async def get_ranking_history(
    recipe_id: int,
    weeks: int = Query(12, ge=1, le=52),
    session=Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Get ranking history for a recipe.

    Args:
        recipe_id (int): Recipe ID
        weeks (int): Number of weeks
        session: Database session
        config (SystemConfig): System configuration

    Returns:
        List[RankingHistory]: Ranking history
    """
    service = VariationService(session, config)
    return service.get_ranking_history(recipe_id, weeks)
