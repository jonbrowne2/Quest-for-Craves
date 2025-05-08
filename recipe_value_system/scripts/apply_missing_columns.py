"""Apply missing columns to the database."""

import os

from sqlalchemy import create_engine, inspect, text

# Create engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")

# Get inspector
inspector = inspect(engine)

# Check if columns exist
columns = [col["name"] for col in inspector.get_columns("vault_recipes")]

# Connect to the database
with engine.connect() as conn:
    # Add parent_recipe_id if it doesn't exist
    if "parent_recipe_id" not in columns:
        print("Adding parent_recipe_id column...")
        conn.execute(
            text(
                """
            ALTER TABLE vault_recipes
            ADD COLUMN parent_recipe_id INTEGER
            REFERENCES vault_recipes(id) ON DELETE SET NULL
        """
            )
        )
    else:
        print("parent_recipe_id already exists.")

    # Add similarity_threshold if it doesn't exist
    if "similarity_threshold" not in columns:
        print("Adding similarity_threshold column...")
        conn.execute(
            text(
                """
            ALTER TABLE vault_recipes
            ADD COLUMN similarity_threshold FLOAT NOT NULL DEFAULT 0.8
        """
            )
        )
    else:
        print("similarity_threshold already exists.")

    # Commit the changes
    conn.commit()

print("Migration completed successfully!")

# Verify the changes
inspector = inspect(engine)
columns = [col["name"] for col in inspector.get_columns("vault_recipes")]
print("\nColumns in vault_recipes after migration:")
print(columns)
