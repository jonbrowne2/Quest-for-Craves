"""Create a recipe using ORM models."""

import json
import os
import sys

from slugify import slugify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import models
from models import Recipe, RecipeCategory, RecipeCategoryAssignment, RecipeTitle
from models.recipe import CuisineType, RecipeStatus

# Create engine and session
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()


def create_recipe():
    """Create a recipe using ORM models."""
    try:
        # Check if recipe already exists
        recipe_slug = slugify("Classic Chocolate Chip Cookies")
        existing_recipe = (
            session.query(Recipe).filter(Recipe.slug == recipe_slug).first()
        )
        if existing_recipe:
            print(
                f"Recipe with slug '{recipe_slug}' already exists, skipping creation."
            )
            return

        # Create recipe
        recipe = Recipe(
            title="Classic Chocolate Chip Cookies",
            slug=recipe_slug,
            status=RecipeStatus.PUBLISHED,
            cuisine_type=CuisineType.AMERICAN,
            ingredients=json.dumps(
                [
                    {
                        "name": "all-purpose flour",
                        "amount": 2.25,
                        "unit": "cups",
                        "notes": None,
                    },
                    {
                        "name": "baking soda",
                        "amount": 1,
                        "unit": "teaspoon",
                        "notes": None,
                    },
                    {"name": "salt", "amount": 1, "unit": "teaspoon", "notes": None},
                    {
                        "name": "unsalted butter",
                        "amount": 1,
                        "unit": "cup",
                        "notes": "softened",
                    },
                    {
                        "name": "brown sugar",
                        "amount": 0.75,
                        "unit": "cup",
                        "notes": "packed",
                    },
                    {
                        "name": "granulated sugar",
                        "amount": 0.75,
                        "unit": "cup",
                        "notes": None,
                    },
                    {
                        "name": "vanilla extract",
                        "amount": 1,
                        "unit": "teaspoon",
                        "notes": None,
                    },
                    {"name": "eggs", "amount": 2, "unit": "large", "notes": None},
                    {
                        "name": "chocolate chips",
                        "amount": 2,
                        "unit": "cups",
                        "notes": "semi-sweet",
                    },
                ]
            ),
            instructions=json.dumps(
                [
                    "Preheat oven to 375°F (190°C).",
                    "In a small bowl, mix flour, baking soda, and salt.",
                    "In a large bowl, cream together butter and sugars until smooth.",
                    "Beat in vanilla and eggs one at a time.",
                    "Gradually blend in the dry ingredients.",
                    "Stir in chocolate chips.",
                    "Drop by rounded tablespoons onto ungreased baking sheets.",
                    "Bake for 9 to 11 minutes or until golden brown.",
                    "Let stand for 2 minutes, then transfer to wire racks to cool completely.",
                ]
            ),
            prep_time=15,
            cook_time=10,
            total_time=35,
            serving_size=24,
            calories_per_serving=150,
            difficulty_score=1.5,
            complexity_score=1.0,
            estimated_cost=5.0,
            seasonal_score=1.0,
            sustainability_score=0.8,
            ai_confidence_score=0.95,
            community_rating=0.0,
            is_deleted=False,
            equipment_needed=json.dumps(
                [
                    "mixing bowls",
                    "measuring cups and spoons",
                    "baking sheets",
                    "wire cooling rack",
                ]
            ),
            macronutrients=json.dumps({"protein": 2, "carbohydrates": 20, "fat": 8}),
        )

        session.add(recipe)
        session.flush()  # Flush to get the recipe ID

        # Create primary title
        primary_title = RecipeTitle(
            recipe_id=recipe.id,
            title="Classic Chocolate Chip Cookies",
            is_primary=True,
            language_code="en",
        )
        session.add(primary_title)

        # Create title variant
        variant_title = RecipeTitle(
            recipe_id=recipe.id,
            title="Traditional American Cookies",
            is_primary=False,
            language_code="en",
        )
        session.add(variant_title)

        # Get or create dessert category
        dessert_category = (
            session.query(RecipeCategory)
            .filter(RecipeCategory.name == "Desserts")
            .first()
        )
        if not dessert_category:
            dessert_category = RecipeCategory(
                name="Desserts", description="Sweet treats and desserts"
            )
            session.add(dessert_category)
            session.flush()

        # Assign recipe to category
        category_assignment = RecipeCategoryAssignment(
            recipe_id=recipe.id,
            category_id=dessert_category.id,
            confidence_score=0.95,
            is_primary=True,
        )
        session.add(category_assignment)

        # Commit the transaction
        session.commit()

        print(
            f"Successfully created recipe 'Classic Chocolate Chip Cookies' with ID {recipe.id}"
        )

    except Exception as e:
        session.rollback()
        print(f"Error creating recipe: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    create_recipe()
