import logging
import sys
from pathlib import Path
from typing import Optional
from config.settings import settings


def setup_logger(
    name: str = "ai_analytics_assistant",
    log_file: Optional[Path] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """Configures and returns a structured Python logger instance.

    Sets up dual stream handlers:
    1. Console Handler (stdout) for real-time monitoring.
    2. File Handler for persistent event logging and debugging.

    Args:
        name: Name of the logger instance (module context).
        log_file: Optional custom file path for log persistence.
        level: Optional log level string (e.g. 'INFO', 'DEBUG').

    Returns:
        logging.Logger: Fully configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent handler duplication if get_logger is called repeatedly
    if logger.hasHandlers():
        return logger

    # Resolve log level from settings or argument
    log_level_str = level or settings.LOG_LEVEL
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Standardized log message format: timestamp - logger name - level - message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Stream Handler for stdout console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler for persistent file logging
    file_path = log_file or settings.LOG_FILE_PATH
    try:
        # Ensure parent directories for log file exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Failed to set up file logger handler: {e}\n")

    # Prevent log propagation to root logger to avoid duplicate log outputs
    logger.propagate = False

    return logger


# Pre-configured application logger instance
logger = setup_logger()
