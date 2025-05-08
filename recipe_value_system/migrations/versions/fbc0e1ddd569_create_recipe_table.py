"""Create initial recipe table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from recipe_value_system.models.recipe import CuisineType, RecipeStatus

# Revision identifiers
revision: str = "fbc0e1ddd569"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recipe table."""
    # Create enums
    recipe_status = sa.Enum(RecipeStatus, name="recipestatus")
    cuisine_type = sa.Enum(CuisineType, name="cuisinetype")

    recipe_status.create(op.get_bind(), checkfirst=True)
    cuisine_type.create(op.get_bind(), checkfirst=True)

    # Create recipe table
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=255), nullable=True),
        sa.Column("status", recipe_status, nullable=False, server_default="PUBLISHED"),
        sa.Column("cuisine_type", cuisine_type, nullable=True),
        sa.Column("dietary_restrictions", sa.JSON(), nullable=True),
        sa.Column("ingredients", sa.JSON(), nullable=False),
        sa.Column("instructions", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
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
    )

    # Create indexes
    op.create_index("idx_recipe_title", "recipes", ["title"])
    op.create_index("idx_recipe_status", "recipes", ["status"])
    op.create_index("idx_recipe_cuisine", "recipes", ["cuisine_type"])


def downgrade() -> None:
    """Remove recipe table."""
    # Drop indexes
    op.drop_index("idx_recipe_cuisine")
    op.drop_index("idx_recipe_status")
    op.drop_index("idx_recipe_title")

    # Drop tables
    op.drop_table("recipes")

    # Drop enums
    sa.Enum(name="recipestatus").drop(op.get_bind())
    sa.Enum(name="cuisinetype").drop(op.get_bind())
