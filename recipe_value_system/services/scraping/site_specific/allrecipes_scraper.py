"""
AllRecipes-specific scraper implementation.

This module provides specialized scraping functionality for AllRecipes website.
"""

import json
import re
from typing import Dict, List

from bs4 import BeautifulSoup

from ..base_scraper import BaseScraper
from ..parsers.ingredient_parser import IngredientParser
from ..parsers.instruction_parser import InstructionParser
from ..recipe_quality import Recipe


class AllRecipesScraper(BaseScraper):
    """
    Scraper for AllRecipes.com to fetch recipe data.

    This class provides methods to scrape recipe data from AllRecipes.com.
    It uses BeautifulSoup to parse HTML and extract relevant information.
    """

    def __init__(self) -> None:
        """
        Initialize the AllRecipes scraper.

        This method sets up the scraper with the necessary attributes.
        """
        super().__init__()
        self.domain = "allrecipes.com"

    def can_handle(self, url: str) -> bool:
        """
        Check if this scraper can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if this scraper can handle the URL
        """
        return self.domain in url

    def scrape(self, url: str) -> Recipe:
        """
        Scrape recipe from AllRecipes URL.

        Args:
            url: AllRecipes URL

        Returns:
            Recipe object
        """
        soup = self.fetch_url(url)
        if not soup:
            raise Exception("Failed to fetch URL")

        # Extract structured data
        structured_data = self._extract_structured_data(soup)

        # Extract basic recipe information
        title = self._extract_title(soup, structured_data)
        description = self._extract_description(soup, structured_data)
        image_url = self._extract_image(soup, structured_data)

        # Extract ingredients and instructions
        ingredients = IngredientParser.extract_from_html(soup)
        instructions = InstructionParser.extract_from_html(soup)

        # Extract metadata
        prep_time = self._extract_prep_time(soup, structured_data)
        cook_time = self._extract_cook_time(soup, structured_data)
        total_time = self._extract_total_time(soup, structured_data)
        servings = self._extract_servings(soup, structured_data)
        calories = self._extract_calories(soup, structured_data)

        # Create recipe object
        recipe = Recipe(
            title=title,
            description=description,
            image_url=image_url,
            ingredients=ingredients,
            instructions=instructions,
            prep_time=prep_time,
            cook_time=cook_time,
            total_time=total_time,
            servings=servings,
            calories=calories,
            url=url,
            source="AllRecipes",
        )

        return recipe

    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract structured data from the page.

        This method extracts JSON-LD data from the page and returns it as a dictionary.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            Dict[str, str]: Structured data extracted from the page.
        """
        structured_data = {}
        script_tags = soup.find_all("script", {"type": "application/ld+json"})

        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if data.get("@type") == "Recipe":
                    structured_data = data
                    break
            except (json.JSONDecodeError, AttributeError):
                continue

        return structured_data

    def _extract_title(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe title.

        This method tries to extract the title from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe title.
        """
        # Try structured data first
        if structured_data.get("name"):
            return structured_data["name"]

        # Try HTML elements
        title_element = soup.find("h1", class_="headline")
        if title_element:
            return title_element.get_text(strip=True)

        return "Untitled Recipe"

    def _extract_description(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe description.

        This method tries to extract the description from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe description.
        """
        # Try structured data first
        if structured_data.get("description"):
            return structured_data["description"]

        # Try HTML elements
        description_element = soup.find("div", class_="summary")
        if description_element:
            return description_element.get_text(strip=True)

        return ""

    def _extract_image(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe image URL.

        This method tries to extract the image URL from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe image URL.
        """
        # Try structured data first
        if structured_data.get("image"):
            image = structured_data["image"]
            if isinstance(image, list) and image:
                return image[0]
            return image

        # Try HTML elements
        image_element = soup.find("img", class_="image")
        if image_element and image_element.get("src"):
            return image_element["src"]

        return ""

    def _extract_prep_time(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe preparation time.

        This method tries to extract the preparation time from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe preparation time.
        """
        # Try structured data first
        if structured_data.get("prepTime"):
            return structured_data["prepTime"]

        # Try HTML elements
        prep_time_element = soup.find("span", class_="prepTime")
        if prep_time_element:
            return prep_time_element.get_text(strip=True)

        return ""

    def _extract_cook_time(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe cooking time.

        This method tries to extract the cooking time from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe cooking time.
        """
        # Try structured data first
        if structured_data.get("cookTime"):
            return structured_data["cookTime"]

        # Try HTML elements
        cook_time_element = soup.find("span", class_="cookTime")
        if cook_time_element:
            return cook_time_element.get_text(strip=True)

        return ""

    def _extract_total_time(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe total time.

        This method tries to extract the total time from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe total time.
        """
        # Try structured data first
        if structured_data.get("totalTime"):
            return structured_data["totalTime"]

        # Try HTML elements
        total_time_element = soup.find("span", class_="totalTime")
        if total_time_element:
            return total_time_element.get_text(strip=True)

        return ""

    def _extract_servings(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe servings.

        This method tries to extract the servings from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe servings.
        """
        # Try structured data first
        if structured_data.get("recipeYield"):
            yield_data = structured_data["recipeYield"]
            if isinstance(yield_data, list) and yield_data:
                return yield_data[0]
            return yield_data

        # Try HTML elements
        servings_element = soup.find("span", class_="servings")
        if servings_element:
            return servings_element.get_text(strip=True)

        return ""

    def _extract_calories(
        self, soup: BeautifulSoup, structured_data: Dict[str, str]
    ) -> str:
        """
        Extract recipe calories.

        This method tries to extract the calories from the structured data first,
        and then from the HTML elements if it's not found.

        Args:
            soup (BeautifulSoup): Parsed HTML content.
            structured_data (Dict[str, str]): Structured data extracted from the page.

        Returns:
            str: Recipe calories.
        """
        # Try structured data first
        if structured_data.get("nutrition") and structured_data["nutrition"].get(
            "calories"
        ):
            return structured_data["nutrition"]["calories"]

        # Try HTML elements
        nutrition_element = soup.find("span", class_="calories")
        if nutrition_element:
            return nutrition_element.get_text(strip=True)

        return ""
