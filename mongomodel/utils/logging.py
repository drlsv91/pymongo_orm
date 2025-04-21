"""
Logging setup for MongoDB ORM.
"""

import logging
import sys
from typing import Optional

from ..config import LOG_FORMAT, DEFAULT_LOG_LEVEL


def setup_logging(
    level: Optional[str] = None, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the MongoDB ORM.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)

    Returns:
        Configured logger instance
    """
    log_level = getattr(logging, level or DEFAULT_LOG_LEVEL)
    logger = logging.getLogger("mongomodel")
    logger.setLevel(log_level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name (will be prefixed with 'mongomodel.')

    Returns:
        Logger instance
    """
    return logging.getLogger(f"mongomodel.{name}")
