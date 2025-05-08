"""Check if models are properly registered."""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import models
from models.base import Base
from models.category import RecipeCategory
from models.category_assignment import RecipeCategoryAssignment
from models.cooking_log import CookingLog
from models.recipe import Recipe
from models.review import RecipeReview
from models.signature import RecipeSignature
from models.title import RecipeTitle

# Create engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Print model attributes
print("Recipe model attributes:")
for attr in dir(Recipe):
    if not attr.startswith("_"):
        print(f"  - {attr}")

# Try to query recipes
try:
    recipes = session.query(Recipe).all()
    print(f"\nFound {len(recipes)} recipes in the database")
    if recipes:
        recipe = recipes[0]
        print(f"First recipe: {recipe.title} (id: {recipe.id})")
        print(
            f"Has parent_recipe_id attribute: {'parent_recipe_id' in recipe.__dict__}"
        )
        print(
            f"Has similarity_threshold attribute: {'similarity_threshold' in recipe.__dict__}"
        )
except Exception as e:
    print(f"\nError querying recipes: {e}")

# Close session
session.close()
