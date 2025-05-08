"""
Test recipe scraping with specific URLs
"""

import logging
import os
import sys
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Add parent directory to path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.scraping.recipe_scraper import EliteRecipeScraper


def test_urls(urls: List[str]):
    """Test scraping specific URLs"""
    scraper = EliteRecipeScraper()

    for url in urls:
        print(f"\nTesting URL: {url}")
        try:
            recipe = scraper.scrape_recipe(url)
            if recipe:
                print("✅ Successfully scraped recipe:")
                print(f"Title: {recipe.title}")
                print(f"Author: {recipe.author}")
                print(f"Ingredients: {len(recipe.ingredients)} items")
                print(f"Steps: {len(recipe.instructions)} steps")
                print("\nQuality Metrics:")
                print(f"Overall Quality: {recipe.metrics.overall_quality:.2f}")
                print(f"Completeness: {recipe.metrics.completeness_score:.2f}")
                print(f"Instruction Clarity: {recipe.metrics.instruction_clarity:.2f}")
                print(f"Ingredient Validity: {recipe.metrics.ingredient_validity:.2f}")
                print(f"Timing Validity: {recipe.metrics.timing_validity:.2f}")
                print(
                    f"Temperature Validity: {recipe.metrics.temperature_validity:.2f}"
                )
                print(f"Portion Consistency: {recipe.metrics.portion_consistency:.2f}")
            else:
                print("❌ Failed to meet quality standards")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    urls = [
        "https://www.theboywhobakes.co.uk/recipes/2018/3/29/j9cnerut0as1ec0fcdiawsc4usi7ss",
        "https://www.kingarthurbaking.com/recipes/apple-pie-recipe",
        "http://www.food.com/recipe/peanut-butter-no-bake-cookies-129040",
    ]
    test_urls(urls)
