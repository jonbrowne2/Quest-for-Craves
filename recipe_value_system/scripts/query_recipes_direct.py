"""Query recipes directly using SQL."""

import json
import os
import sqlite3

# Create connection
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()


def pretty_print_json(json_str):
    """Pretty print JSON string."""
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2)
    except:
        return json_str


def query_recipes():
    """Query recipes and their relationships."""
    try:
        # Get all recipes
        cursor.execute(
            """
            SELECT * FROM vault_recipes
        """
        )
        recipes = cursor.fetchall()

        print(f"Found {len(recipes)} recipes")

        for recipe in recipes:
            print(f"\nRecipe ID: {recipe['id']}")
            print(f"  Title: {recipe['title']}")
            print(f"  Slug: {recipe['slug']}")
            print(f"  Status: {recipe['status']}")
            print(f"  Created At: {recipe['created_at']}")

            if recipe["parent_recipe_id"]:
                cursor.execute(
                    """
                    SELECT title FROM vault_recipes WHERE id = ?
                """,
                    (recipe["parent_recipe_id"],),
                )
                parent = cursor.fetchone()
                if parent:
                    print(
                        f"  Parent Recipe: {parent['title']} (ID: {recipe['parent_recipe_id']})"
                    )
                print(f"  Similarity Threshold: {recipe['similarity_threshold']}")

            # Get recipe titles
            cursor.execute(
                """
                SELECT * FROM recipe_titles WHERE recipe_id = ?
            """,
                (recipe["id"],),
            )
            titles = cursor.fetchall()

            print(f"  Titles ({len(titles)}):")
            for title in titles:
                print(
                    f"    - {title['title']} (Primary: {bool(title['is_primary'])}, Language: {title['language_code']})"
                )

            # Get category assignments
            cursor.execute(
                """
                SELECT rca.*, rc.name
                FROM recipe_category_assignments rca
                JOIN recipe_categories rc ON rca.category_id = rc.id
                WHERE rca.recipe_id = ?
            """,
                (recipe["id"],),
            )
            assignments = cursor.fetchall()

            print(f"  Categories ({len(assignments)}):")
            for assignment in assignments:
                print(
                    f"    - {assignment['name']} (Primary: {bool(assignment['is_primary'])}, Confidence: {assignment['confidence_score']})"
                )

            # Get recipe variants
            cursor.execute(
                """
                SELECT id, title FROM vault_recipes WHERE parent_recipe_id = ?
            """,
                (recipe["id"],),
            )
            variants = cursor.fetchall()

            if variants:
                print(f"  Variants ({len(variants)}):")
                for variant in variants:
                    print(f"    - {variant['title']} (ID: {variant['id']})")

            # Print some of the JSON fields
            print("\n  Ingredients:")
            print(pretty_print_json(recipe["ingredients"]))

            print("\n  Instructions:")
            print(pretty_print_json(recipe["instructions"]))

            if recipe["equipment_needed"]:
                print("\n  Equipment Needed:")
                print(pretty_print_json(recipe["equipment_needed"]))

            if recipe["macronutrients"]:
                print("\n  Macronutrients:")
                print(pretty_print_json(recipe["macronutrients"]))

            print("\n" + "-" * 80)

    except Exception as e:
        print(f"Error querying recipes: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    query_recipes()
