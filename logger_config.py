"""Logging Configuration Module.

This module configures and provides a centralized logger using the `loguru` library.
It reads logging settings from a TOML configuration file, sets up a custom log format,
and ensures the log directory exists. The configured logger can be imported and used
across the application for consistent logging.

Features:
- Loads logging configuration from a TOML file.
- Creates the log directory if it doesn't exist.
- Configures `loguru` with a custom log format, rotation, compression, and log level.
- Provides a `get_logger` function to retrieve the configured logger instance.

Usage:
1. Ensure a `config.toml` file exists with a `[logging]` section containing:
   - `log_file_name`: Path to the log file.
   - `log_rotation`: Log rotation policy (e.g., "10 MB").
   - `log_compression`: Log compression format (e.g., "zip").
   - `min_log_level`: Minimum log level (e.g., "INFO").
2. Import the `get_logger` function from this module to use the configured logger.

Example:
    ```python
    from .logging_config import get_logger

    logger = get_logger()
    logger.info("This is an info message.")
    ```

Dependencies:
- `loguru`: For advanced logging features.
- `toml`: For reading the configuration file.
- `pathlib`: For handling file system operations.

"""

from pathlib import Path

import toml
from loguru import logger

# Load configuration from TOML file
config = toml.load("config.toml")

# Extract logging configuration
log_config = config["logging"]

# Ensure log directory exists
log_file_path = Path(log_config["log_file_name"])
log_file_path.parent.mkdir(parents=True, exist_ok=True)

# Define a custom log format
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level} | "
    "{module}:{function}:{line} - {message}"
)

# Configure Loguru
logger.remove()  # Remove default logger
logger.add(
    str(log_file_path),  # Convert Path to string for compatibility
    format=LOG_FORMAT,  # Custom format added here
    rotation=log_config["log_rotation"],
    compression=log_config["log_compression"],
    level=log_config["min_log_level"],
    backtrace=True,
    diagnose=True,
)

def get_logger() -> logger:
    """Return the logger instance for use in other files."""
    return logger

# Example usage
if __name__ == "__main__":
    logger.info("Logger configured successfully.")
