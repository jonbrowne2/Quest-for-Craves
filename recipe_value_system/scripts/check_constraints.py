"""Check table constraints."""

import os
import sqlite3

# Create connection
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(vault_recipes)")
columns = cursor.fetchall()

print("Columns in vault_recipes table:")
for col in columns:
    col_id, name, type_, not_null, default, pk = col
    print(
        f"  - {name} ({type_}), NOT NULL: {bool(not_null)}, DEFAULT: {default}, PK: {bool(pk)}"
    )

# Close connection
conn.close()
