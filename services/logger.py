from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from config import settings

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Console Logger
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
)

# File Logger
logger.add(
    LOG_DIR / "app.log",
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)


class AppLogger:
    """
    Wrapper around Loguru to keep logging
    consistent across the application.
    """

    @staticmethod
    def info(message: str):
        logger.info(message)

    @staticmethod
    def warning(message: str):
        logger.warning(message)

    @staticmethod
    def error(message: str):
        logger.error(message)

    @staticmethod
    def debug(message: str):
        logger.debug(message)

    @staticmethod
    def exception(message: str):
        logger.exception(message)


app_logger = AppLogger()