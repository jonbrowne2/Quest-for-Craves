"""Create recipes table with indexes.

Revision ID: 001
Revises: 
Create Date: 2025-03-21 21:28:31.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recipes table with indexes."""
    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('ingredients', sqlite.JSON(), nullable=False),
        sa.Column('steps', sqlite.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('prep_time', sa.Integer(), nullable=True),
        sa.Column('cook_time', sa.Integer(), nullable=True),
        sa.Column('votes', sqlite.JSON(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('complexity', sa.Float(), nullable=True),
        sa.Column('mob_score', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_recipes_name', 'recipes', ['name'])
    op.create_index('ix_recipes_created_at', 'recipes', ['created_at'])
    op.create_index('ix_recipes_rating', 'recipes', ['rating'])
    op.create_index('ix_recipes_mob_score', 'recipes', ['mob_score'])


def downgrade() -> None:
    """Drop recipes table and indexes."""
    op.drop_index('ix_recipes_mob_score')
    op.drop_index('ix_recipes_rating')
    op.drop_index('ix_recipes_created_at')
    op.drop_index('ix_recipes_name')
    op.drop_table('recipes')
