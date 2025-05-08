"""
Elite recipe scraper that can handle various sources
and focuses on high-quality recipes.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from .parsers.ingredient_parser import IngredientParser
from .parsers.instruction_parser import InstructionParser
from .recipe_quality import Recipe, RecipeQualityAnalyzer
from .site_specific import AllRecipesScraper


class EliteRecipeScraper:
    """
    High-quality recipe scraper that can handle various sources.

    This scraper delegates to specialized scrapers based on the source URL
    and applies quality analysis to ensure only high-quality recipes are returned.
    """

    def __init__(self) -> None:
        """Initialize the elite recipe scraper."""
        self.logger = logging.getLogger(__name__)
        self.scrapers = self._register_scrapers()
        self.base_scraper = BaseScraper()
        self.quality_analyzer = RecipeQualityAnalyzer()

    def _register_scrapers(self) -> List[BaseScraper]:
        """
        Register all available specialized scrapers.

        Returns:
            List of registered scrapers
        """
        return [
            AllRecipesScraper(),
            # Add more specialized scrapers here
        ]

    def scrape_recipe(self, source: Dict[str, Any]) -> Optional[Recipe]:
        """
        Scrape a recipe from various sources and validate quality.

        Args:
            source: Dictionary containing recipe data

        Returns:
            Recipe object if quality standards are met, None otherwise
        """
        try:
            # Handle different source types
            if isinstance(source, dict):
                recipe = self._parse_recipe_dict(source)
            else:
                self.logger.warning(f"Unsupported source type: {type(source)}")
                return None

            # Apply quality analysis
            if recipe:
                quality_metrics = self.quality_analyzer.analyze(recipe)
                recipe.quality_metrics = quality_metrics

                # Only return recipes that meet quality standards
                if self._meets_quality_standards(quality_metrics):
                    return recipe
                else:
                    self.logger.info(
                        f"Recipe '{recipe.title}' did not meet quality standards"
                    )

            return None

        except Exception as e:
            self.logger.error(f"Error scraping recipe: {e}")
            return None

    def _parse_recipe_dict(self, data: Dict[str, Any]) -> Optional[Recipe]:
        """
        Parse recipe from a dictionary (structured data or API response).

        Args:
            data: Dictionary containing recipe data

        Returns:
            Recipe object or None if parsing failed
        """
        try:
            # Handle both direct recipe data and nested data
            recipe_data = data
            if "@graph" in data:
                for item in data["@graph"]:
                    if item.get("@type") == "Recipe":
                        recipe_data = item
                        break

            # Extract basic recipe information
            title = recipe_data.get("name", "Untitled Recipe")

            # Extract ingredients
            ingredients = []
            raw_ingredients = recipe_data.get(
                "recipeIngredient", []
            ) or recipe_data.get("ingredients", [])
            if isinstance(raw_ingredients, str):
                raw_ingredients = [raw_ingredients]

            for ingredient in raw_ingredients:
                if isinstance(ingredient, str):
                    ingredients.append({"text": ingredient.strip()})
                elif isinstance(ingredient, dict):
                    ingredients.append(ingredient)

            # Extract instructions
            instructions = []
            raw_instructions = recipe_data.get(
                "recipeInstructions", []
            ) or recipe_data.get("instructions", [])

            if isinstance(raw_instructions, str):
                instructions.append({"text": raw_instructions.strip(), "position": 1})
            else:
                for i, instruction in enumerate(raw_instructions):
                    if isinstance(instruction, str):
                        instructions.append(
                            {"text": instruction.strip(), "position": i + 1}
                        )
                    elif isinstance(instruction, dict):
                        text = instruction.get("text", "")
                        if text:
                            instructions.append(
                                {"text": text.strip(), "position": i + 1}
                            )

            # Create recipe object
            recipe = Recipe(
                title=title,
                description=recipe_data.get("description", ""),
                image_url=recipe_data.get("image", ""),
                ingredients=ingredients,
                instructions=instructions,
                prep_time=recipe_data.get("prepTime", ""),
                cook_time=recipe_data.get("cookTime", ""),
                total_time=recipe_data.get("totalTime", ""),
                servings=recipe_data.get("recipeYield", ""),
                calories=recipe_data.get("nutrition", {}).get("calories", ""),
                url=recipe_data.get("url", ""),
                source=recipe_data.get("publisher", {}).get("name", "Unknown"),
            )

            return recipe

        except Exception as e:
            self.logger.error(f"Error parsing recipe dictionary: {e}")
            return None

    def _meets_quality_standards(self, metrics: Dict[str, Any]) -> bool:
        """
        Check if recipe meets quality standards.

        Args:
            metrics: Quality metrics dictionary

        Returns:
            True if recipe meets quality standards
        """
        # Implement your quality standards here
        min_ingredient_count = 3
        min_instruction_count = 2

        ingredient_count = metrics.get("ingredient_count", 0)
        instruction_count = metrics.get("instruction_count", 0)

        return (
            ingredient_count >= min_ingredient_count
            and instruction_count >= min_instruction_count
        )
