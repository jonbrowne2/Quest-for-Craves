"""Check recipe relationships."""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.category import RecipeCategory
from models.category_assignment import RecipeCategoryAssignment

# Import models
from models.recipe import Recipe
from models.title import RecipeTitle

# Create engine and session
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()


def check_recipes():
    """Check recipes and their relationships."""
    try:
        # Get all recipes
        recipes = session.query(Recipe).all()
        print(f"Found {len(recipes)} recipes")

        for recipe in recipes:
            print(f"\nRecipe ID: {recipe.id}")
            print(f"  Title: {recipe.title}")
            print(f"  Slug: {recipe.slug}")
            print(f"  Status: {recipe.status}")
            print(f"  Created At: {recipe.created_at}")

            # Check titles
            print(f"  Titles ({len(recipe.titles)}):")
            for title in recipe.titles:
                print(
                    f"    - {title.title} (Primary: {title.is_primary}, Language: {title.language_code})"
                )

            # Check category assignments
            print(f"  Categories ({len(recipe.category_assignments)}):")
            for assignment in recipe.category_assignments:
                category = assignment.category
                print(
                    f"    - {category.name} (Primary: {assignment.is_primary}, Confidence: {assignment.confidence_score})"
                )

            # Check parent/variant relationship
            if recipe.parent_recipe_id:
                parent = session.query(Recipe).get(recipe.parent_recipe_id)
                print(f"  Parent Recipe: {parent.title} (ID: {parent.id})")
                print(f"  Similarity Threshold: {recipe.similarity_threshold}")

            # Check variants
            variants = (
                session.query(Recipe).filter(Recipe.parent_recipe_id == recipe.id).all()
            )
            if variants:
                print(f"  Variants ({len(variants)}):")
                for variant in variants:
                    print(f"    - {variant.title} (ID: {variant.id})")

    except Exception as e:
        print(f"Error checking recipes: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    check_recipes()
