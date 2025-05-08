"""Main entry point for the Recipe Value System."""

import logging
import os
from typing import Optional

from pydantic import BaseModel, Field

from .analytics.analytics_service import AnalyticsService
from .config import get_config
from .config.logging_config import setup_logging


class AppStatus(BaseModel):
    """Application status information.

    Attributes:
        status (str): Current application status
        environment (str): Current environment
        version (str): Application version
        debug_mode (bool): Debug mode status
    """

    status: str = Field(default="running", description="Current application status")
    environment: str = Field(default="development", description="Current environment")
    version: str = Field(default="0.1.0", description="Application version")
    debug_mode: bool = Field(default=False, description="Debug mode status")


def initialize_app(env: Optional[str] = None) -> AppStatus:
    """Initialize the Recipe Value System application.

    Args:
        env: Optional environment name

    Returns:
        Application status information
    """
    # Load configuration
    config = get_config(env or "development")

    # Set up logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info(
        "Starting Recipe Value System " f"v{config.version} in {config.env} mode"
    )

    # Initialize analytics service
    analytics_service = AnalyticsService(config=config)
    analytics_service.start()

    return AppStatus(
        status="running",
        environment=config.env,
        version=config.version,
        debug_mode=config.debug_mode,
    )


if __name__ == "__main__":
    # Get environment from ENV var or use development
    env = os.getenv("RECIPE_VALUE_ENV", "development")
    status = initialize_app(env)
    print(f"Application status: {status.model_dump()}")
