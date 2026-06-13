"""
Logging setup — structured JSON logs via Loguru.

Call `configure_logging()` once at application startup.
"""
from __future__ import annotations

import sys

from loguru import logger

from mrif.config import settings


def configure_logging() -> None:
    """
    Configure Loguru with the log level from settings.

    In production set MRIF_LOG_LEVEL=WARNING or ERROR.
    """
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
    logger.add(
        "mrif.log",
        level="DEBUG",
        format="{time} | {level} | {name}:{line} — {message}",
        rotation="10 MB",
        retention="7 days",
        compression="gz",
        serialize=True,   # JSON format in the file
    )
    logger.info(f"Logging configured: level={settings.log_level}")
