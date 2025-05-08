"""Example configuration usage for the Recipe Value System."""

from typing import Dict, Optional

from recipe_value_system.config import get_config
from recipe_value_system.config.logging_config import setup_logging


def initialize_app(env: Optional[str] = None) -> Dict[str, str]:
    """Initialize application with configuration.

    Args:
        env: Optional environment name

    Returns:
        Dictionary containing initialization status
    """
    # Load configuration
    config = get_config(env or "development")

    # Set up logging
    setup_logging(config)

    return {
        "status": "success",
        "environment": config.env,
        "app_name": config.app_name,
        "version": config.version,
    }


if __name__ == "__main__":
    # Example usage
    status = initialize_app("development")
    print(f"Application initialized: {status}")
