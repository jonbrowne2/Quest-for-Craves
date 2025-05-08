"""Check vault_recipes table schema."""

import os

from sqlalchemy import create_engine, inspect

# Create engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")

# Get inspector
inspector = inspect(engine)

# Check vault_recipes columns
columns = inspector.get_columns("vault_recipes")
print("Columns in vault_recipes:")
for column in columns:
    print(f"  - {column['name']} ({column['type']})")

# Check if parent_recipe_id exists
has_parent_id = any(col["name"] == "parent_recipe_id" for col in columns)
print(f"\nHas parent_recipe_id column: {has_parent_id}")

# Check if similarity_threshold exists
has_similarity = any(col["name"] == "similarity_threshold" for col in columns)
print(f"Has similarity_threshold column: {has_similarity}")
