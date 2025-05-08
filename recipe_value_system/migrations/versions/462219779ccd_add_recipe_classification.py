"""Add recipe classification tables and relationships.

Revision ID: 462219779ccd
Revises: 8f21118b35cf
Create Date: 2025-02-25 13:30:11.317055

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Revision identifiers
revision: str = "462219779ccd"
down_revision: Union[str, None] = "8f21118b35cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recipe classification tables."""
    # Create recipe_categories table for high-level categorization
    op.create_table(
        "recipe_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_category_id", sa.Integer(), nullable=True),
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
            ["parent_category_id"], ["recipe_categories.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("name"),
    )

    # Create recipe_signatures table for ingredient/method fingerprints
    op.create_table(
        "recipe_signatures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column(
            "key_ingredients", sa.JSON(), nullable=False
        ),  # Core ingredients that define the recipe type
        sa.Column(
            "method_signature", sa.JSON(), nullable=False
        ),  # Key cooking methods/techniques used
        sa.Column(
            "texture_profile", sa.JSON(), nullable=False
        ),  # Expected texture characteristics
        sa.Column(
            "timing_profile", sa.JSON(), nullable=False
        ),  # Expected timing ranges
        sa.Column(
            "confidence_score", sa.Float(), nullable=False
        ),  # How confident we are in this classification
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
            ["recipe_id"], ["vault_recipes.id"], ondelete="CASCADE"
        ),
    )

    # Create recipe_category_assignments table
    op.create_table(
        "recipe_category_assignments",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"),
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
        sa.PrimaryKeyConstraint("recipe_id", "category_id"),
        sa.ForeignKeyConstraint(
            ["recipe_id"], ["vault_recipes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["category_id"], ["recipe_categories.id"], ondelete="CASCADE"
        ),
    )

    # Add similarity_threshold to vault_recipes
    op.add_column(
        "vault_recipes",
        sa.Column(
            "similarity_threshold", sa.Float(), nullable=False, server_default="0.8"
        ),
    )

    # Create indexes
    op.create_index(
        "idx_recipe_categories_parent", "recipe_categories", ["parent_category_id"]
    )
    op.create_index("idx_recipe_signatures_recipe", "recipe_signatures", ["recipe_id"])
    op.create_index(
        "idx_category_assignments_recipe", "recipe_category_assignments", ["recipe_id"]
    )
    op.create_index(
        "idx_category_assignments_category",
        "recipe_category_assignments",
        ["category_id"],
    )

    # Create unique constraint for primary category
    op.create_index(
        "uix_recipe_primary_category",
        "recipe_category_assignments",
        ["recipe_id", "is_primary"],
        unique=True,
        sqlite_where=sa.text("is_primary = 1"),
    )

    # Insert some basic categories
    op.execute(
        """
        INSERT INTO recipe_categories (name, description) VALUES
        ('Cookies', 'Sweet, baked, usually flat pastries'),
        ('Pasta Dishes', 'Dishes where pasta is the primary component'),
        ('Breads', 'Baked goods made from dough'),
        ('Pastries', 'Light, flaky baked goods'),
        ('Cakes', 'Sweet baked desserts'),
        ('Soups', 'Liquid dishes combining various ingredients'),
        ('Salads', 'Cold dishes primarily composed of vegetables'),
        ('Main Dishes', 'Primary course meals'),
        ('Side Dishes', 'Accompanying dishes'),
        ('Desserts', 'Sweet dishes typically served after meals'),
        ('Breakfast', 'Morning meals'),
        ('Beverages', 'Drinks and liquid refreshments')
    """
    )


def downgrade() -> None:
    """Remove recipe classification tables."""
    # Drop indexes
    op.drop_index("idx_recipe_categories_parent")
    op.drop_index("idx_recipe_signatures_recipe")
    op.drop_index("idx_category_assignments_recipe")
    op.drop_index("idx_category_assignments_category")
    op.drop_index("uix_recipe_primary_category")

    # Drop tables
    op.drop_table("recipe_category_assignments")
    op.drop_table("recipe_signatures")
    op.drop_table("recipe_categories")

    # Drop columns
    op.drop_column("vault_recipes", "similarity_threshold")
