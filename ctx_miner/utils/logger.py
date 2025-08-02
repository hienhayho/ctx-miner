"""Logger configuration for ctx-miner using loguru."""

import logging
from loguru import logger
import sys
from typing import Optional


def setup_logger(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
    colorize: bool = True,
    backtrace: bool = True,
    diagnose: bool = True,
):
    """
    Set up loguru logger configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom format string (uses default if None)
        log_file: Optional log file path
        colorize: Whether to colorize console output
        backtrace: Whether to show backtrace in errors
        diagnose: Whether to show variable values in errors
    """
    # Remove default handler
    logging.basicConfig(level=level)
    logger.remove()

    # Default format
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler
    logger.add(
        sys.stdout,
        format=format_string,
        level=level,
        colorize=colorize,
        backtrace=backtrace,
        diagnose=diagnose,
        enqueue=True,
    )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format=format_string,
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            backtrace=backtrace,
            diagnose=diagnose,
            enqueue=True,
        )
        logger.info(f"Logging to file: {log_file}")

    logger.info(f"Logger initialized with level: {level}")


def get_logger(name: str = "ctx-miner"):
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
