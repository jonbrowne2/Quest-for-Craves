"""Insert a recipe directly using SQL."""

import json
import os

from slugify import slugify
from sqlalchemy import create_engine, text

# Create engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")


def insert_recipe():
    """Insert a recipe directly using SQL."""
    try:
        # Connect to the database
        with engine.connect() as conn:
            # Check if recipe already exists
            recipe_slug = slugify("Homemade Pizza Dough")
            result = conn.execute(
                text("SELECT id FROM vault_recipes WHERE slug = :slug"),
                {"slug": recipe_slug},
            )
            if result.fetchone():
                print(
                    f"Recipe with slug '{recipe_slug}' already exists, skipping insertion."
                )
                return

            # Insert recipe
            result = conn.execute(
                text(
                    """
                    INSERT INTO vault_recipes (
                        title, slug, status, ingredients, instructions,
                        prep_time, cook_time, total_time, serving_size,
                        calories_per_serving, difficulty_score, complexity_score,
                        estimated_cost, seasonal_score, sustainability_score,
                        ai_confidence_score, community_rating, cuisine_type,
                        dietary_preferences, equipment_needed, macronutrients,
                        created_at, updated_at, is_deleted
                    ) VALUES (
                        :title, :slug, :status, :ingredients, :instructions,
                        :prep_time, :cook_time, :total_time, :serving_size,
                        :calories, :difficulty, :complexity, :cost, :seasonal,
                        :sustainability, :ai_confidence, :rating, :cuisine,
                        :dietary, :equipment, :macros, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
                    )
                """
                ),
                {
                    "title": "Homemade Pizza Dough",
                    "slug": recipe_slug,
                    "status": "PUBLISHED",
                    "ingredients": json.dumps(
                        [
                            {
                                "name": "all-purpose flour",
                                "amount": 3,
                                "unit": "cups",
                                "notes": "plus more for dusting",
                            },
                            {
                                "name": "active dry yeast",
                                "amount": 2.25,
                                "unit": "teaspoons",
                                "notes": "1 packet",
                            },
                            {
                                "name": "warm water",
                                "amount": 1,
                                "unit": "cup",
                                "notes": "105-110°F",
                            },
                            {
                                "name": "salt",
                                "amount": 1,
                                "unit": "teaspoon",
                                "notes": None,
                            },
                            {
                                "name": "olive oil",
                                "amount": 2,
                                "unit": "tablespoons",
                                "notes": "plus more for coating",
                            },
                            {
                                "name": "sugar",
                                "amount": 1,
                                "unit": "teaspoon",
                                "notes": None,
                            },
                        ]
                    ),
                    "instructions": json.dumps(
                        [
                            "Combine water, sugar, and yeast in a bowl. Let sit for 5 minutes until foamy.",
                            "Mix in salt and olive oil.",
                            "Gradually add flour and mix until a soft dough forms.",
                            "Knead for 5-7 minutes until smooth and elastic.",
                            "Place in an oiled bowl, cover, and let rise for 1 hour.",
                            "Punch down, divide into two balls, and let rest for 10 minutes.",
                            "Roll out and top as desired.",
                            "Bake at 475°F for 10-12 minutes.",
                        ]
                    ),
                    "prep_time": 20,
                    "cook_time": 12,
                    "total_time": 92,
                    "serving_size": 2,
                    "calories": 250,
                    "difficulty": 2.5,
                    "complexity": 2.0,
                    "cost": 3.0,
                    "seasonal": 1.0,
                    "sustainability": 0.9,
                    "ai_confidence": 0.95,
                    "rating": 0.0,
                    "cuisine": "ITALIAN",
                    "dietary": json.dumps(
                        {
                            "suitable_for": ["vegetarian"],
                            "meal_type": ["dinner", "lunch"],
                        }
                    ),
                    "equipment": json.dumps(
                        [
                            "mixing bowl",
                            "measuring cups and spoons",
                            "baking sheet",
                            "rolling pin",
                        ]
                    ),
                    "macros": json.dumps({"protein": 7, "carbohydrates": 42, "fat": 5}),
                },
            )
            recipe_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()

            # Insert recipe signature
            conn.execute(
                text(
                    """
                    INSERT INTO recipe_signatures (
                        recipe_id, key_ingredients, method_signature, texture_profile,
                        timing_profile, confidence_score, created_at, updated_at
                    ) VALUES (
                        :recipe_id, :key_ingredients, :method_signature, :texture_profile,
                        :timing_profile, :confidence, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                ),
                {
                    "recipe_id": recipe_id,
                    "key_ingredients": json.dumps(
                        {
                            "required": [
                                "flour",
                                "yeast",
                                "water",
                                "salt",
                                "olive oil",
                            ],
                            "proportions": {
                                "flour_to_water": 3.0,
                                "yeast_to_flour": 0.01,
                            },
                        }
                    ),
                    "method_signature": json.dumps(
                        ["mixing", "kneading", "rising", "shaping", "baking"]
                    ),
                    "texture_profile": json.dumps(
                        {
                            "exterior": "crispy",
                            "interior": "chewy",
                            "thickness": "medium",
                        }
                    ),
                    "timing_profile": json.dumps(
                        {
                            "prep_time_minutes": {"min": 15, "max": 25},
                            "rise_time_minutes": {"min": 60, "max": 90},
                            "bake_time_minutes": {"min": 10, "max": 15},
                            "total_time_minutes": {"min": 85, "max": 120},
                        }
                    ),
                    "confidence": 0.95,
                },
            )

            # Get or create pizza category
            result = conn.execute(
                text("SELECT id FROM recipe_categories WHERE name = 'Pizza'")
            )
            category_row = result.fetchone()

            if category_row:
                category_id = category_row[0]
            else:
                conn.execute(
                    text(
                        """
                        INSERT INTO recipe_categories (name, description, created_at, updated_at)
                        VALUES ('Pizza', 'Flatbread with toppings', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                    )
                )
                category_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()

            # Assign recipe to category
            conn.execute(
                text(
                    """
                    INSERT INTO recipe_category_assignments (
                        recipe_id, category_id, confidence_score, is_primary, created_at, updated_at
                    ) VALUES (
                        :recipe_id, :category_id, :confidence, :is_primary, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                ),
                {
                    "recipe_id": recipe_id,
                    "category_id": category_id,
                    "confidence": 0.95,
                    "is_primary": 1,
                },
            )

            # Add primary title
            conn.execute(
                text(
                    """
                    INSERT INTO recipe_titles (
                        recipe_id, title, is_primary, language_code, created_at, updated_at
                    ) VALUES (
                        :recipe_id, :title, :is_primary, :language_code, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                ),
                {
                    "recipe_id": recipe_id,
                    "title": "Homemade Pizza Dough",
                    "is_primary": 1,
                    "language_code": "en",
                },
            )

            # Add a title variant
            conn.execute(
                text(
                    """
                    INSERT INTO recipe_titles (
                        recipe_id, title, is_primary, language_code, created_at, updated_at
                    ) VALUES (
                        :recipe_id, :title, :is_primary, :language_code, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                ),
                {
                    "recipe_id": recipe_id,
                    "title": "Basic Pizza Crust",
                    "is_primary": 0,
                    "language_code": "en",
                },
            )

            # Commit the transaction
            conn.commit()

            print(
                f"Successfully inserted recipe 'Homemade Pizza Dough' with ID {recipe_id}"
            )

    except Exception as e:
        print(f"Error inserting recipe: {e}")


if __name__ == "__main__":
    insert_recipe()
