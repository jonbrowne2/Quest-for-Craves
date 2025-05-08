"""
Ingredient parsing module for the recipe value system.

This module provides utilities for parsing and standardizing recipe ingredients.
"""

import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag


class IngredientParser:
    """Parser for extracting and normalizing recipe ingredients."""

    @staticmethod
    def extract_from_html(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract ingredients from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of ingredient dictionaries
        """
        ingredient_selectors = [
            '[itemprop="recipeIngredient"]',
            ".ingredients li",
            ".ingredient-list li",
            ".recipe-ingredients li",
            "#ingredients li",
            ".ingredient",
            "[data-ingredient]",
        ]

        ingredients = []

        # Try specific ingredient selectors
        for selector in ingredient_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = IngredientParser.extract_text_content(element)
                    if text and len(text) > 2:  # Avoid very short ingredients
                        ingredients.append({"text": text})
                return ingredients

        # Fallback to JSON-LD data
        script_tags = soup.find_all("script", {"type": "application/ld+json"})
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if data.get("@type") == "Recipe" and "recipeIngredient" in data:
                    return [{"text": ing} for ing in data["recipeIngredient"]]
            except (json.JSONDecodeError, AttributeError):
                continue

        return ingredients

    @staticmethod
    def extract_text_content(element: Tag) -> str:
        """
        Extract clean text content from an HTML element.

        Args:
            element: BeautifulSoup Tag

        Returns:
            Cleaned text content
        """
        text = element.get_text(strip=True)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def parse_quantity(text: str) -> Dict[str, Any]:
        """
        Parse ingredient quantity from text.

        Args:
            text: Ingredient text

        Returns:
            Dictionary with parsed quantity information
        """
        # Basic quantity extraction
        quantity_pattern = r"^(\d+[\d./]*)(?:\s+(\w+))?\s+"
        match = re.match(quantity_pattern, text)

        if match:
            amount = match.group(1)
            unit = match.group(2) if match.group(2) else ""
            ingredient = text[match.end() :].strip()
            return {
                "text": text,
                "amount": amount,
                "unit": unit,
                "ingredient": ingredient,
            }

        return {"text": text}
