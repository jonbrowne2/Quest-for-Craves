import json
import os

from slugify import slugify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.category import RecipeCategory
from models.category_assignment import RecipeCategoryAssignment
from models.cooking_log import CookingLog
from models.recipe import CuisineType, Recipe, RecipeStatus
from models.review import RecipeReview
from models.signature import RecipeSignature
from models.title import RecipeTitle

# Create engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")

# Create all tables
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()


def insert_recipe_and_signature():
    try:
        # Check if recipe already exists
        recipe_slug = slugify("Classic Chocolate Chip Cookies")
        existing_recipe = session.query(Recipe).filter_by(slug=recipe_slug).first()

        if existing_recipe:
            print(
                f"Recipe with slug '{recipe_slug}' already exists, skipping insertion."
            )
            return

        # Create recipe
        recipe = Recipe(
            title="Classic Chocolate Chip Cookies",
            slug=slugify("Classic Chocolate Chip Cookies"),
            status=RecipeStatus.PUBLISHED,
            ingredients=json.dumps(
                [
                    {
                        "name": "all-purpose flour",
                        "amount": 2.25,
                        "unit": "cups",
                        "notes": "sifted",
                    },
                    {"name": "butter", "amount": 1, "unit": "cup", "notes": "softened"},
                    {
                        "name": "granulated sugar",
                        "amount": 0.75,
                        "unit": "cup",
                        "notes": None,
                    },
                    {
                        "name": "brown sugar",
                        "amount": 0.75,
                        "unit": "cup",
                        "notes": "packed",
                    },
                    {
                        "name": "eggs",
                        "amount": 2,
                        "unit": "whole",
                        "notes": "room temperature",
                    },
                    {
                        "name": "vanilla extract",
                        "amount": 1,
                        "unit": "teaspoon",
                        "notes": None,
                    },
                    {
                        "name": "baking soda",
                        "amount": 1,
                        "unit": "teaspoon",
                        "notes": None,
                    },
                    {"name": "salt", "amount": 0.5, "unit": "teaspoon", "notes": None},
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
                    "Cream butter and sugars",
                    "Beat in eggs and vanilla",
                    "Mix dry ingredients",
                    "Fold in chocolate chips",
                    "Drop onto baking sheet",
                    "Bake at 375°F for 10-12 minutes",
                ]
            ),
            prep_time=15,
            cook_time=12,
            total_time=27,
            serving_size=24,
            calories_per_serving=150,
            difficulty_score=2.0,
            complexity_score=1.5,
            estimated_cost=10.0,
            seasonal_score=1.0,
            sustainability_score=0.8,
            ai_confidence_score=0.95,
            community_rating=0.0,
            cuisine_type=CuisineType.AMERICAN,
            dietary_preferences=json.dumps(
                {
                    "suitable_for": ["sweet_tooth", "kid_friendly"],
                    "meal_type": ["dessert", "snack"],
                }
            ),
            equipment_needed=json.dumps(
                [
                    "mixing bowls",
                    "electric mixer",
                    "baking sheet",
                    "measuring cups and spoons",
                ]
            ),
            macronutrients=json.dumps({"protein": 2, "carbohydrates": 25, "fat": 8}),
        )

        session.add(recipe)
        session.commit()

        # Create recipe signature
        signature = RecipeSignature(
            recipe_id=recipe.id,
            key_ingredients=json.dumps(
                {
                    "required": ["flour", "butter", "sugar", "eggs", "chocolate chips"],
                    "proportions": {
                        "flour_to_butter": 2.25,
                        "sugar_to_flour": 0.67,
                        "chips_to_dough": 0.3,
                    },
                }
            ),
            method_signature=json.dumps(
                ["creaming", "mixing", "folding", "dropping", "baking"]
            ),
            texture_profile=json.dumps(
                {
                    "exterior": "crispy",
                    "interior": "chewy",
                    "chocolate": "melted",
                    "thickness": "medium",
                }
            ),
            timing_profile=json.dumps(
                {
                    "prep_time_minutes": {"min": 10, "max": 15},
                    "bake_time_minutes": {"min": 10, "max": 12},
                    "total_time_minutes": {"min": 20, "max": 30},
                }
            ),
            confidence_score=0.95,
        )

        session.add(signature)

        # Get cookie category
        category = session.query(RecipeCategory).filter_by(name="Cookies").first()
        if not category:
            print("Warning: 'Cookies' category not found. Creating it.")
            category = RecipeCategory(
                name="Cookies", description="Sweet, baked, usually flat pastries"
            )
            session.add(category)
            session.commit()

        # Assign recipe to category
        category_assignment = RecipeCategoryAssignment(
            recipe_id=recipe.id,
            category_id=category.id,
            confidence_score=0.95,
            is_primary=True,
        )
        session.add(category_assignment)

        # Add a title variant
        title_variant = RecipeTitle(
            recipe_id=recipe.id,
            title="Traditional Chocolate Chip Cookies",
            is_primary=False,
            language_code="en",
        )
        session.add(title_variant)

        # Add primary title
        primary_title = RecipeTitle(
            recipe_id=recipe.id, title=recipe.title, is_primary=True, language_code="en"
        )
        session.add(primary_title)

        session.commit()
        print("Successfully inserted recipe and all related data!")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    insert_recipe_and_signature()
