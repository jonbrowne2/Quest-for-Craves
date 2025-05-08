"""Database management script."""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from alembic import command
from alembic.config import Config

from recipe_value_system.config import SystemConfig


def main():
    """Run database migrations."""
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")

    # Load environment variables
    config = SystemConfig()

    # Set the database URL
    os.environ["DATABASE_URL"] = config.db.URL

    # Create the versions directory if it doesn't exist
    versions_path = Path("migrations/versions")
    versions_path.mkdir(exist_ok=True)

    try:
        # Generate a new migration
        command.revision(
            alembic_cfg,
            autogenerate=True,
            message="Add indexes for performance optimization",
        )
        print("Migration file created successfully!")
    except Exception as e:
        print(f"Error creating migration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
