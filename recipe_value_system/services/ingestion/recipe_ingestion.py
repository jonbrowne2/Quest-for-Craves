"""Service for ingesting and processing scraped recipes."""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from recipe_value_system.models.recipe import CuisineType, Recipe
from recipe_value_system.services.scraping.recipe_scraper import ScrapedRecipe
from recipe_value_system.value.calculator import RecipeValueCalculator


class RecipeIngestionService:
    """
    Service for handling recipe ingestion operations.

    Attributes:
        session (Session): SQLAlchemy session object
        config (Any): Configuration object
        logger (Logger): Logger instance
        value_calculator (RecipeValueCalculator): Recipe value calculator instance
    """

    def __init__(self, session: Session, config: Any):
        """
        Initialize the RecipeIngestionService.

        Args:
            session (Session): SQLAlchemy session object
            config (Any): Configuration object
        """
        self.session = session
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.value_calculator = RecipeValueCalculator(session, config)

    def ingest_recipe(self, scraped_recipe: ScrapedRecipe) -> Optional[Recipe]:
        """
        Ingest a scraped recipe into the system.

        Args:
            scraped_recipe (ScrapedRecipe): ScrapedRecipe object containing recipe data

        Returns:
            Recipe object if successful, None if failed
        """
        try:
            # Create slug from title
            slug = self._create_slug(scraped_recipe.title)

            # Convert cuisine type
            cuisine_type = self._map_cuisine_type(scraped_recipe.cuisine_type)

            # Create recipe object
            recipe = Recipe(
                title=scraped_recipe.title,
                slug=slug,
                source_url=scraped_recipe.source_url,
                cuisine_type=cuisine_type,
                ingredients=self._process_ingredients(scraped_recipe.ingredients),
                instructions=self._process_instructions(scraped_recipe.instructions),
                serving_size=scraped_recipe.servings,
                prep_time=scraped_recipe.prep_time,
                cook_time=scraped_recipe.cook_time,
                total_time=scraped_recipe.total_time,
                calories_per_serving=scraped_recipe.calories,
                macronutrients={
                    "protein": scraped_recipe.protein,
                    "carbs": scraped_recipe.carbs,
                    "fat": scraped_recipe.fat,
                },
                community_rating=scraped_recipe.rating,
                review_count=scraped_recipe.review_count or 0,
                metadata={
                    "image_url": scraped_recipe.image_url,
                    "author": scraped_recipe.author,
                    "tags": scraped_recipe.tags,
                    "scraped_at": scraped_recipe.scraped_at.isoformat(),
                },
            )

            # Calculate initial value scores
            self._calculate_initial_scores(recipe)

            # Save to database
            self.session.add(recipe)
            self.session.commit()

            self.logger.info(f"Successfully ingested recipe: {recipe.title}")
            return recipe

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error ingesting recipe {scraped_recipe.title}: {str(e)}"
            )
            return None

    def _create_slug(self, title: str) -> str:
        """
        Create URL-friendly slug from title.

        Args:
            title (str): Recipe title

        Returns:
            str: Slug string
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower().replace(" ", "-")
        # Remove special characters
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        return slug

    def _map_cuisine_type(self, cuisine: Optional[str]) -> Optional[CuisineType]:
        """
        Map string cuisine type to enum.

        Args:
            cuisine (Optional[str]): Cuisine type string

        Returns:
            Optional[CuisineType]: CuisineType enum or None
        """
        if not cuisine:
            return None

        cuisine = cuisine.lower()
        cuisine_map = {
            "italian": CuisineType.ITALIAN,
            "mexican": CuisineType.MEXICAN,
            "chinese": CuisineType.CHINESE,
            "japanese": CuisineType.JAPANESE,
            "indian": CuisineType.INDIAN,
            "french": CuisineType.FRENCH,
            "mediterranean": CuisineType.MEDITERRANEAN,
            "american": CuisineType.AMERICAN,
            "thai": CuisineType.THAI,
            "vietnamese": CuisineType.VIETNAMESE,
            "korean": CuisineType.KOREAN,
            "middle eastern": CuisineType.MIDDLE_EASTERN,
        }

        return cuisine_map.get(cuisine)

    def _process_ingredients(self, ingredients: List[Dict]) -> List[Dict]:
        """
        Process and standardize ingredients.

        Args:
            ingredients (List[Dict]): List of ingredient dictionaries

        Returns:
            List[Dict]: List of processed ingredient dictionaries
        """
        processed = []
        for ing in ingredients:
            processed.append(
                {
                    "amount": ing.get("amount"),
                    "unit": self._standardize_unit(ing.get("unit", "")),
                    "name": ing.get("name", "").lower(),
                    "original": ing.get("original_text", ""),
                }
            )
        return processed

    def _standardize_unit(self, unit: str) -> str:
        """
        Standardize measurement units.

        Args:
            unit (str): Unit string

        Returns:
            str: Standardized unit string
        """
        unit = unit.lower().strip()
        unit_map = {
            "tablespoon": "tbsp",
            "tablespoons": "tbsp",
            "tbsp.": "tbsp",
            "teaspoon": "tsp",
            "teaspoons": "tsp",
            "tsp.": "tsp",
            "pound": "lb",
            "pounds": "lb",
            "ounce": "oz",
            "ounces": "oz",
            "gram": "g",
            "grams": "g",
            "kilogram": "kg",
            "kilograms": "kg",
            "milliliter": "ml",
            "milliliters": "ml",
            "liter": "l",
            "liters": "l",
            "cup": "cup",
            "cups": "cup",
        }
        return unit_map.get(unit, unit)

    def _process_instructions(self, instructions: List[str]) -> List[Dict]:
        """
        Process and enhance instructions.

        Args:
            instructions (List[str]): List of instruction strings

        Returns:
            List[Dict]: List of processed instruction dictionaries
        """
        processed = []
        for i, step in enumerate(instructions, 1):
            processed.append(
                {
                    "step": i,
                    "text": step,
                    "time_estimate": self._extract_time_from_step(step),
                }
            )
        return processed

    def _extract_time_from_step(self, step: str) -> Optional[int]:
        """
        Extract cooking time from instruction step.

        Args:
            step (str): Instruction step string

        Returns:
            Optional[int]: Cooking time in minutes or None
        """
        time_patterns = [r"(\d+)\s*(?:minute|min)", r"(\d+)\s*(?:hour|hr)"]

        total_minutes = 0
        for pattern in time_patterns:
            match = re.search(pattern, step, re.I)
            if match:
                amount = int(match.group(1))
                if "hour" in pattern:
                    total_minutes += amount * 60
                else:
                    total_minutes += amount

        return total_minutes if total_minutes > 0 else None

    def _calculate_initial_scores(self, recipe: Recipe) -> None:
        """
        Calculate initial recipe scores.

        Args:
            recipe (Recipe): Recipe object
        """
        # Difficulty score based on number of ingredients and steps
        recipe.difficulty_score = min(
            5.0,
            (
                len(recipe.ingredients) * 0.2
                + len(recipe.instructions) * 0.3
                + (recipe.total_time or 0) / 60.0
            ),
        )

        # Complexity score based on unique ingredients and techniques
        recipe.complexity_score = min(
            5.0,
            (
                len(set(ing["name"] for ing in recipe.ingredients)) * 0.3
                + len(recipe.instructions) * 0.2
            ),
        )

        # Estimated cost (placeholder - would need ingredient price database)
        recipe.estimated_cost = len(recipe.ingredients) * 2.0  # rough estimate

        # Seasonal score (placeholder - would need ingredient seasonality data)
        recipe.seasonal_score = 3.0  # neutral score

        # Sustainability score (placeholder - would need ingredient sustainability data)
        recipe.sustainability_score = 3.0  # neutral score

        # AI confidence score based on data completeness
        recipe.ai_confidence_score = self._calculate_confidence_score(recipe)

    def _calculate_confidence_score(self, recipe: Recipe) -> float:
        """
        Calculate AI confidence score based on data completeness.

        Args:
            recipe (Recipe): Recipe object

        Returns:
            float: Confidence score between 0 and 1
        """
        # TO DO: implement confidence score calculation
        return 0.5  # placeholder
