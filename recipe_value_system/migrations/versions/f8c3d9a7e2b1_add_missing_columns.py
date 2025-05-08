"""Add missing columns to vault recipes table.

Revision ID: f8c3d9a7e2b1
Revises: 462219779ccd
Create Date: 2025-02-25 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Revision identifiers
revision: str = "f8c3d9a7e2b1"
down_revision: Union[str, None] = "462219779ccd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to vault recipes table."""
    # Get inspector
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check if columns exist before adding them
    columns = [col["name"] for col in inspector.get_columns("vault_recipes")]

    # Add parent_recipe_id if it doesn't exist
    if "parent_recipe_id" not in columns:
        op.add_column(
            "vault_recipes", sa.Column("parent_recipe_id", sa.Integer(), nullable=True)
        )
        op.create_foreign_key(
            "fk_recipe_parent",
            "vault_recipes",
            "vault_recipes",
            ["parent_recipe_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # Add similarity_threshold if it doesn't exist
    if "similarity_threshold" not in columns:
        op.add_column(
            "vault_recipes",
            sa.Column(
                "similarity_threshold", sa.Float(), nullable=False, server_default="0.8"
            ),
        )

    # Create index for parent_recipe_id
    op.create_index("idx_recipe_parent", "vault_recipes", ["parent_recipe_id"])


def downgrade() -> None:
    """Remove added columns from vault recipes table."""
    # Drop index
    op.drop_index("idx_recipe_parent", table_name="vault_recipes")

    # Drop foreign key constraint
    op.drop_constraint("fk_recipe_parent", "vault_recipes", type_="foreignkey")

    # Drop columns
    op.drop_column("vault_recipes", "parent_recipe_id")
    op.drop_column("vault_recipes", "similarity_threshold")
