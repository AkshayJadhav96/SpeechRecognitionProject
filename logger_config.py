from loguru import logger
import os

# Load configuration (these can be stored in a separate config file)
LOG_FILE_NAME = "logs/application.log"
LOG_ROTATION = "1h"  # Rotate logs every 24 hours
LOG_COMPRESSION = "zip"  # Compress old logs into zip files
LOG_LEVEL = "INFO"  # Change to DEBUG for more logs

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_NAME), exist_ok=True)

# Define a custom log format
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"

# Configure Loguru
logger.remove()  # Remove default logger
logger.add(
    LOG_FILE_NAME, 
    format=LOG_FORMAT,  # Custom format added here
    rotation=LOG_ROTATION, 
    compression=LOG_COMPRESSION, 
    level=LOG_LEVEL, 
    backtrace=True, 
    diagnose=True
)

def get_logger():
    return logger  # Return the logger instance for use in other files
