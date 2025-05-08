"""Database migration script for the Recipe Value System."""

import logging
import os
from typing import Optional

from alembic import command, config
from sqlalchemy import create_engine

from recipe_value_system.config import get_config
from recipe_value_system.models import Base

# Set up logging
logger = logging.getLogger(__name__)


def run_migrations(env: Optional[str] = None) -> None:
    """Run database migrations.

    Args:
        env: Optional environment name.
    """
    # Load configuration
    app_config = get_config(env or "development")

    # Get database URL
    db_url = app_config.get_database_url()

    # Create engine and tables
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    # Get alembic config
    alembic_cfg = config.Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Run migrations
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Successfully ran database migrations")
    except Exception:
        logger.error(
            "Failed to run database migrations",
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    # Get environment from ENV var or use development
    env = os.getenv("RECIPE_VALUE_ENV", "development")
    run_migrations(env)
