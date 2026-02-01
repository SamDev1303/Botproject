"""
Logging configuration for all MCP servers

Provides standardized logging with:
- Rotating file handlers (10MB max, 5 backups)
- Console output for development
- Consistent formatting
- Automatic log directory creation
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os


def setup_logging(name: str, log_dir: Path = None, level: str = None) -> logging.Logger:
    """
    Configure logging for MCP servers

    Args:
        name: Logger name (typically __name__ from calling module)
        log_dir: Directory for log files (default: ~/.clawdbot/logs/mcp/)
        level: Logging level (default: INFO, or from LOG_LEVEL env var)

    Returns:
        Configured logger instance

    Example:
        >>> from mcp.logging_config import setup_logging
        >>> logger = setup_logging(__name__)
        >>> logger.info("Server started successfully")
        >>> logger.error(f"Failed to process request: {error}")
    """
    # Default log directory
    if log_dir is None:
        log_dir = Path.home() / ".clawdbot" / "logs" / "mcp"

    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Determine log level from environment or parameter
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()

    # Convert string level to logging constant
    numeric_level = getattr(logging, level, logging.INFO)

    # Extract simple name from full module path (e.g., "mcp.square_server" -> "square_server")
    simple_name = name.split('.')[-1] if '.' in name else name
    log_file = log_dir / f"{simple_name}.log"

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Avoid adding handlers multiple times if logger already exists
    if logger.handlers:
        return logger

    # Rotating file handler (10MB max, 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler for real-time monitoring
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an already configured logger by name

    Args:
        name: Logger name

    Returns:
        Existing logger instance, or creates new one if not found
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logging(name)
    return logger
