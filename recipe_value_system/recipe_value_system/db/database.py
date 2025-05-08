"""Database configuration and session management."""
import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

# Ensure data directory exists
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

# Database configuration
DB_PATH = data_dir / "cravequest.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

def get_engine(url: Optional[str] = None) -> Engine:
    """Get SQLAlchemy engine instance.
    
    Args:
        url: Optional database URL, defaults to DATABASE_URL
        
    Returns:
        SQLAlchemy Engine instance
    """
    return create_engine(url or DATABASE_URL)

def get_session_maker(engine: Optional[Engine] = None) -> sessionmaker:
    """Get SQLAlchemy session maker.
    
    Args:
        engine: Optional engine instance, creates new one if not provided
        
    Returns:
        Session maker configured with engine
    """
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine)

# Default session maker
SessionMaker = get_session_maker()

def get_session() -> Session:
    """Get a new database session.
    
    Returns:
        New SQLAlchemy Session instance
    """
    return SessionMaker()
