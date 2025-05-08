"""Migrations configuration."""
import os
from pathlib import Path
from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

def get_db_url() -> str:
    """Get database URL for migrations.
    
    Returns:
        Database URL string
    """
    # Get base directory (repository root)
    base_dir = Path(__file__).parent.parent
    
    # Create data directory if it doesn't exist
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Use absolute path for SQLite database
    db_path = data_dir / "cravequest.db"
    return f"sqlite:///{db_path.absolute()}"

def get_engine() -> Engine:
    """Get SQLAlchemy engine for migrations.
    
    Returns:
        SQLAlchemy engine
    """
    url = get_db_url()
    return create_engine(
        url,
        # Enable SQLite foreign key support
        connect_args={"check_same_thread": False},
        # Print SQL statements for debugging
        echo=True
    )

def get_session() -> Session:
    """Get SQLAlchemy session for migrations.
    
    Returns:
        SQLAlchemy session
    """
    engine = get_engine()
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    return SessionLocal()
