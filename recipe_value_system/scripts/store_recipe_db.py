"""Store recipe in database."""

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import Session, init_db
from models.recipe_vault import Recipe


def store_recipe(recipe_json_path):
    """Store recipe from JSON file in database."""
    # Read recipe JSON
    with open(recipe_json_path, "r") as f:
        recipe_data = json.load(f)

    # Create recipe object
    recipe = Recipe(
        name=recipe_data["title"],
        ingredients=recipe_data["ingredients"],
        instructions=recipe_data["instructions"],
        cooking_time=(
            int(recipe_data.get("total_time", "0").split()[0])
            if recipe_data.get("total_time")
            else None
        ),
        serving_size=int(recipe_data.get("yields", 0)),
        nutritional_info={},  # We'll need to calculate this
        difficulty_level="INTERMEDIATE",  # We can make this smarter
        cuisine_type="AMERICAN",  # We can make this smarter
        dietary_restrictions=[],  # We'll need to analyze ingredients
        dietary_preferences={},
        estimated_cost=None,  # We'll need to calculate this
        flavor_profile={},  # We'll need to analyze ingredients
        texture_profile={},  # We'll need to analyze instructions
        seasonal_tags=[],  # We can make this smarter
    )

    # Store in database
    session = Session()
    try:
        session.add(recipe)
        session.commit()
        print(f"Successfully stored recipe: {recipe.name}")
    except Exception as e:
        session.rollback()
        print(f"Error storing recipe: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python store_recipe_db.py <recipe_json_path>")
        sys.exit(1)

    recipe_json_path = sys.argv[1]
    if not os.path.exists(recipe_json_path):
        print(f"Recipe file not found: {recipe_json_path}")
        sys.exit(1)

    # Initialize database if needed
    init_db()

    # Store recipe
    store_recipe(recipe_json_path)
