"""Test script for recipe scraper."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from services.scraping.recipe_scraper import AllRecipesScraper


def test_scraper():
    """Test the recipe scraper with a few different recipes."""
    scraper = AllRecipesScraper()

    # Test URLs
    urls = [
        "https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/",
        "https://www.allrecipes.com/recipe/158968/spinach-and-feta-turkey-burgers/",
        "https://www.allrecipes.com/recipe/20144/banana-banana-bread/",
        "https://www.allrecipes.com/recipe/20175/quick-and-easy-biscuits/",
    ]

    recipes = []
    for url in urls:
        try:
            recipe = scraper.scrape_recipe(url)
            print(f"Successfully scraped: {recipe.title}")
            print(f"Ingredients: {len(recipe.ingredients)}")
            print(f"Instructions: {len(recipe.instructions)}")
            print("-" * 50)
            recipes.append(recipe)
        except Exception as e:
            print(f"Failed to scrape {url}: {str(e)}")
            continue

    # Save to JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"scraped_recipes_{timestamp}.json"

    # Convert recipes to JSON-serializable format
    recipes_data = []
    for recipe in recipes:
        recipe_dict = {
            "title": recipe.title,
            "source_url": recipe.source_url,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "total_time": recipe.total_time,
            "servings": recipe.servings,
            "cuisine_type": recipe.cuisine_type,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "carbs": recipe.carbs,
            "fat": recipe.fat,
            "image_url": recipe.image_url,
            "author": recipe.author,
            "rating": recipe.rating,
            "review_count": recipe.review_count,
            "tags": recipe.tags,
            "scraped_at": recipe.scraped_at.isoformat(),
            "source_attribution": recipe.source_attribution,
        }
        recipes_data.append(recipe_dict)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recipes_data, f, indent=2, ensure_ascii=False)

    print(f"\nRaw data saved to {output_file}")


if __name__ == "__main__":
    test_scraper()
