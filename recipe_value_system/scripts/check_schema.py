"""Check database schema."""

import json
import os

from sqlalchemy import create_engine, inspect

# Create engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
engine = create_engine(f"sqlite:///{db_path}")

# Get inspector
inspector = inspect(engine)

# Get all tables
tables = inspector.get_table_names()
print("Tables in database:", tables)

# Check each table's columns
for table_name in tables:
    columns = inspector.get_columns(table_name)
    print(f"\nColumns in {table_name}:")
    for column in columns:
        print(f"  - {column['name']} ({column['type']})")

    # Get foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name)
    if foreign_keys:
        print(f"\nForeign keys in {table_name}:")
        for fk in foreign_keys:
            print(
                f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
            )

    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print(f"\nIndexes in {table_name}:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['column_names']} (unique: {idx['unique']})")
