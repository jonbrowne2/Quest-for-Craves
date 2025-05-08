"""Add recipe variants and titles to the database.

Revision ID: 8f21118b35cf
Revises: fbc0e1ddd569
Create Date: 2025-02-23 21:16:06.317055

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Revision identifiers
revision: str = "8f21118b35cf"
down_revision: Union[str, None] = "fbc0e1ddd569"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recipe variants and titles tables."""
    # Get inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # Drop existing tables if they exist
    if "recipe_titles" in tables:
        op.drop_table("recipe_titles")
    if "vault_recipes_new" in tables:
        op.drop_table("vault_recipes_new")

    # Create recipe_titles table for alternative titles
    op.create_table(
        "recipe_titles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("language_code", sa.String(length=5), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["vault_recipes.id"],
            name="fk_recipe_titles_recipe",
            ondelete="CASCADE",
        ),
    )

    # Create new vault_recipes table with parent_recipe_id
    op.execute(
        """
        CREATE TABLE vault_recipes_new (
            id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            slug VARCHAR NOT NULL,
            source_url VARCHAR,
            status VARCHAR NOT NULL DEFAULT 'PUBLISHED',
            cuisine_type VARCHAR,
            dietary_restrictions JSON,
            dietary_preferences JSON,
            ingredients JSON NOT NULL,
            instructions JSON NOT NULL,
            equipment_needed JSON,
            serving_size INTEGER,
            prep_time INTEGER,
            cook_time INTEGER,
            total_time INTEGER,
            calories_per_serving FLOAT,
            macronutrients JSON,
            micronutrients JSON,
            difficulty_score FLOAT,
            complexity_score FLOAT,
            estimated_cost FLOAT,
            seasonal_score FLOAT,
            sustainability_score FLOAT,
            ai_confidence_score FLOAT,
            community_rating FLOAT,
            review_count INTEGER NOT NULL DEFAULT 0,
            favorite_count INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME,
            parent_recipe_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(parent_recipe_id) REFERENCES vault_recipes_new(id) ON DELETE SET NULL
        )
    """
    )

    # Copy data from old table to new table
    if "vault_recipes" in tables:
        op.execute(
            """
            INSERT INTO vault_recipes_new (
                id, title, slug, source_url, status, cuisine_type,
                dietary_restrictions, dietary_preferences, ingredients,
                instructions, equipment_needed, serving_size, prep_time,
                cook_time, total_time, calories_per_serving, macronutrients,
                micronutrients, difficulty_score, complexity_score,
                estimated_cost, seasonal_score, sustainability_score,
                ai_confidence_score, community_rating, review_count,
                favorite_count, created_at, updated_at, deleted_at,
                parent_recipe_id
            )
            SELECT
                id, title, slug, source_url, status, cuisine_type,
                dietary_restrictions, dietary_preferences, ingredients,
                instructions, equipment_needed, serving_size, prep_time,
                cook_time, total_time, calories_per_serving, macronutrients,
                micronutrients, difficulty_score, complexity_score,
                estimated_cost, seasonal_score, sustainability_score,
                ai_confidence_score, community_rating, review_count,
                favorite_count, created_at, updated_at, deleted_at,
                NULL as parent_recipe_id
            FROM vault_recipes
        """
        )
        op.drop_table("vault_recipes")

    op.rename_table("vault_recipes_new", "vault_recipes")

    # Create indexes
    op.create_index("idx_recipe_titles_recipe", "recipe_titles", ["recipe_id"])
    op.create_index("idx_recipe_titles_title", "recipe_titles", ["title"])
    op.create_index("idx_recipe_titles_language", "recipe_titles", ["language_code"])
    op.create_index("idx_recipe_parent", "vault_recipes", ["parent_recipe_id"])
    op.create_index("idx_recipe_status", "vault_recipes", ["status"])
    op.create_index("idx_recipe_title", "vault_recipes", ["title"])
    op.create_index("idx_recipe_slug", "vault_recipes", ["slug"], unique=True)
    op.create_index("idx_recipe_cuisine", "vault_recipes", ["cuisine_type"])
    op.create_index("idx_recipe_created", "vault_recipes", ["created_at"])
    op.create_index("idx_recipe_updated", "vault_recipes", ["updated_at"])

    # Create unique constraint for primary titles
    op.execute(
        """
        CREATE UNIQUE INDEX uix_recipe_titles_primary
        ON recipe_titles(recipe_id)
        WHERE is_primary = 1
    """
    )

    # Migrate existing titles to recipe_titles table
    op.execute(
        """
        INSERT INTO recipe_titles (recipe_id, title, is_primary, created_at, updated_at)
        SELECT id, title, 1, created_at, updated_at
        FROM vault_recipes
    """
    )


def downgrade() -> None:
    """Remove recipe variants and titles tables."""
    # Create new vault_recipes table without parent_recipe_id
    op.execute(
        """
        CREATE TABLE vault_recipes_new (
            id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            slug VARCHAR NOT NULL,
            source_url VARCHAR,
            status VARCHAR NOT NULL DEFAULT 'PUBLISHED',
            cuisine_type VARCHAR,
            dietary_restrictions JSON,
            dietary_preferences JSON,
            ingredients JSON NOT NULL,
            instructions JSON NOT NULL,
            equipment_needed JSON,
            serving_size INTEGER,
            prep_time INTEGER,
            cook_time INTEGER,
            total_time INTEGER,
            calories_per_serving FLOAT,
            macronutrients JSON,
            micronutrients JSON,
            difficulty_score FLOAT,
            complexity_score FLOAT,
            estimated_cost FLOAT,
            seasonal_score FLOAT,
            sustainability_score FLOAT,
            ai_confidence_score FLOAT,
            community_rating FLOAT,
            review_count INTEGER NOT NULL DEFAULT 0,
            favorite_count INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME,
            PRIMARY KEY (id)
        )
    """
    )

    # Copy data from old table to new table
    op.execute(
        """
        INSERT INTO vault_recipes_new
        SELECT id, title, slug, source_url, status, cuisine_type,
               dietary_restrictions, dietary_preferences, ingredients,
               instructions, equipment_needed, serving_size, prep_time,
               cook_time, total_time, calories_per_serving, macronutrients,
               micronutrients, difficulty_score, complexity_score,
               estimated_cost, seasonal_score, sustainability_score,
               ai_confidence_score, community_rating, review_count,
               favorite_count, created_at, updated_at, deleted_at
        FROM vault_recipes
    """
    )

    # Drop old table and recipe_titles
    op.drop_table("vault_recipes")
    op.drop_table("recipe_titles")

    # Rename new table to vault_recipes
    op.rename_table("vault_recipes_new", "vault_recipes")

    # Recreate indexes
    op.create_index("idx_recipe_status", "vault_recipes", ["status"])
    op.create_index("idx_recipe_title", "vault_recipes", ["title"])
    op.create_index("idx_recipe_slug", "vault_recipes", ["slug"], unique=True)
    op.create_index("idx_recipe_cuisine", "vault_recipes", ["cuisine_type"])
    op.create_index("idx_recipe_created", "vault_recipes", ["created_at"])
    op.create_index("idx_recipe_updated", "vault_recipes", ["updated_at"])
