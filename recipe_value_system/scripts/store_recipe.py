"""Script to store a recipe in our vault."""

import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def clean_time(time_str: str) -> str:
    """Clean up time string."""
    if not time_str:
        return None
    # Extract just the number of minutes
    match = re.search(r"(\d+)\s*minutes?", time_str.lower())
    if match:
        return f"{match.group(1)} minutes"
    return time_str


def clean_text(text: str) -> str:
    """Clean up text content."""
    if not text:
        return None
    # Remove extra whitespace and normalize quotes
    return " ".join(text.strip().split())


def fetch_recipe(url: str) -> dict:
    """Fetch recipe from URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Try to get recipe data from HTML
    recipe = {
        "source_url": url,
        "user_rating": "Crave",  # As specified by user
        "scraped_at": datetime.utcnow().isoformat(),
    }

    # Get title
    title = soup.select_one("h1.entry-title")
    if title:
        recipe["title"] = clean_text(title.get_text())

    # Get ingredients
    ingredients = []
    for item in soup.select(".wprm-recipe-ingredient"):
        amount = item.select_one(".wprm-recipe-ingredient-amount")
        unit = item.select_one(".wprm-recipe-ingredient-unit")
        name = item.select_one(".wprm-recipe-ingredient-name")
        notes = item.select_one(".wprm-recipe-ingredient-notes")

        parts = []
        if amount:
            parts.append(clean_text(amount.get_text()))
        if unit:
            parts.append(clean_text(unit.get_text()))
        if name:
            parts.append(clean_text(name.get_text()))
        if notes:
            parts.append(f"({clean_text(notes.get_text())})")

        if parts:
            ingredients.append(" ".join(parts))

    recipe["ingredients"] = ingredients

    # Get instructions
    instructions = []
    for step in soup.select(".wprm-recipe-instruction-text"):
        text = clean_text(step.get_text())
        if text:
            instructions.append(text)

    recipe["instructions"] = instructions

    # Get times
    prep_time = soup.select_one(".wprm-recipe-prep-time-container")
    if prep_time:
        recipe["prep_time"] = clean_time(prep_time.get_text())

    cook_time = soup.select_one(".wprm-recipe-cook-time-container")
    if cook_time:
        recipe["cook_time"] = clean_time(cook_time.get_text())

    total_time = soup.select_one(".wprm-recipe-total-time-container")
    if total_time:
        recipe["total_time"] = clean_time(total_time.get_text())

    # Get yield
    servings = soup.select_one(".wprm-recipe-servings")
    if servings:
        recipe["yields"] = clean_text(servings.get_text())

    # Get author
    author = soup.select_one(".wprm-recipe-author")
    if author:
        recipe["author"] = clean_text(author.get_text())
    else:
        recipe["author"] = "Sam @ Sugar Spun Run"  # Default author for this site

    # Set source attribution
    recipe["source_attribution"] = f"Recipe from {recipe['author']} at {url}"

    return recipe


def store_recipe(recipe: dict):
    """Store recipe in our vault."""
    vault_dir = Path(__file__).parent.parent / "vault" / "recipes"
    vault_dir.mkdir(parents=True, exist_ok=True)

    # Create a filename from the recipe title
    if recipe.get("title"):
        filename = recipe["title"].lower().replace(" ", "_") + ".json"
    else:
        filename = "untitled_recipe.json"
    filepath = vault_dir / filename

    # Store the recipe
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(recipe, f, indent=2, ensure_ascii=False)

    return filepath


def main():
    url = "https://sugarspunrun.com/worst-chocolate-chip-cookies/"
    recipe = fetch_recipe(url)
    if recipe.get("title") and recipe.get("ingredients") and recipe.get("instructions"):
        filepath = store_recipe(recipe)
        print(f"Successfully stored recipe at: {filepath}")
        print("\nRecipe details:")
        print(json.dumps(recipe, indent=2, ensure_ascii=False))
    else:
        print("Failed to fetch complete recipe")
        print("Available data:", json.dumps(recipe, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
