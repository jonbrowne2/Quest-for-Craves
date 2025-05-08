"""Module for handling recipe data imports via web scraping."""

import json
from typing import Optional

import requests
from bs4 import BeautifulSoup

from models.recipe import Recipe


def scrape_recipe(url: str) -> Optional[Recipe]:
    """Scrape a recipe from a URL and return a Recipe object."""
    try:
        # Fetch the page
        headers = {"User-Agent": "Mozilla/5.0"}  # Avoid bot detection
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        soup = BeautifulSoup(response.text, "html.parser")

        # Try Schema.org/Recipe JSON-LD first (common standard)
        script_tags = soup.find_all("script", type="application/ld+json")
        for script in script_tags:
            try:
                data = json.loads(script.string)
                # Handle case where JSON-LD is a list or single dict
                if isinstance(data, list):
                    data = next(
                        (item for item in data if item.get("@type") == "Recipe"), None
                    )
                if data and data.get("@type") == "Recipe":
                    name = data.get("name", "Unknown Recipe")
                    ingredients = data.get("recipeIngredient", [])
                    steps = [
                        step["text"]
                        for step in data.get("recipeInstructions", [])
                        if "text" in step
                    ]

                    # Parse times (e.g., "PT30M" -> 30 minutes)
                    prep_time = parse_time(data.get("prepTime", "PT0M"))
                    cook_time = parse_time(data.get("cookTime", "PT0M"))
                    servings = (
                        int(data.get("recipeYield", 1))
                        if data.get("recipeYield")
                        else 1
                    )

                    return Recipe(
                        name, ingredients, steps, prep_time, cook_time, servings
                    )
            except json.JSONDecodeError:
                continue

        # Fallback: Parse HTML (basic heuristic, site-specific tweaks later)
        name = soup.find("h1") or "Unknown Recipe"
        name = name.text.strip() if name else "Unknown Recipe"

        # Look for common ingredient list classes
        ingred_list = soup.find(
            class_=["ingredient-list", "ingredients", "recipe-ingredients"]
        )
        ingredients = (
            [li.text.strip() for li in ingred_list.find_all("li")]
            if ingred_list
            else ["Unknown"]
        )

        # Look for common instruction list classes
        steps_list = soup.find(class_=["instructions", "recipe-instructions", "method"])
        steps = (
            [li.text.strip() for li in steps_list.find_all("li")]
            if steps_list
            else ["Unknown"]
        )

        # Guess times and servings (crude, improve later)
        prep_time = 0  # Placeholder
        cook_time = 0  # Placeholder
        servings = 1  # Default

        return Recipe(name, ingredients, steps, prep_time, cook_time, servings)

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def parse_time(time_str: str) -> int:
    """Convert ISO 8601 duration (e.g., PT30M) to minutes."""
    if not time_str or "PT" not in time_str:
        return 0
    minutes = 0
    if "H" in time_str:
        hours = int(time_str.split("PT")[1].split("H")[0])
        minutes += hours * 60
    if "M" in time_str:
        m_part = time_str.split("H")[-1] if "H" in time_str else time_str.split("PT")[1]
        minutes += int(m_part.split("M")[0])
    return minutes


if __name__ == "__main__":
    # Test it
    url = "https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/"
    recipe = scrape_recipe(url)
    if recipe:
        print(f"Name: {recipe.name}")
        print(f"Ingredients: {recipe.ingredients}")
        print(f"Steps: {recipe.steps}")
        print(f"Prep Time: {recipe.prep_time} min")
        print(f"Cook Time: {recipe.cook_time} min")
        print(f"Servings: {recipe.servings}")
