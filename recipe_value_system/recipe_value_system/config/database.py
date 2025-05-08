"""Database configuration."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base

# Get database URL from environment or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vault/recipes.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
Session = sessionmaker(bind=engine)


def init_db():
    """Initialize the database schema."""
    # Create all tables
    Base.metadata.create_all(engine)


def get_session():
    """Get a new database session."""
    return Session()
