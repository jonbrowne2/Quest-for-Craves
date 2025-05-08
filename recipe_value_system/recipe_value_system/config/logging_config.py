"""Logging configuration module for the Recipe Value System."""

import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .config import SystemConfig


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )
    file: Optional[str] = Field(default=None, description="Log file path")
    console: bool = Field(default=True, description="Enable console logging")


def setup_logging(config: Optional[SystemConfig] = None) -> None:
    """Set up logging configuration.

    Args:
        config: Optional system configuration

    Returns:
        None
    """
    if not config:
        config = SystemConfig()

    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": config.log_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": config.log_level,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": config.log_level,
                "propagate": True,
            },
        },
    }

    # Add file handler if log file is specified
    log_file = os.environ.get("RECIPE_VALUE_LOG_FILE")
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        log_config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "filename": log_file,
            "formatter": "standard",
            "level": config.log_level,
        }
        log_config["loggers"][""]["handlers"].append("file")

    logging.config.dictConfig(log_config)
