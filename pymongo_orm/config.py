"""
Configuration settings for MongoDB ORM.
"""

from typing import Any, Dict

# Connection defaults
DEFAULT_BATCH_SIZE = 100
DEFAULT_TIMEOUT_MS = 30000  # 30 seconds
DEFAULT_MAX_POOL_SIZE = 100
DEFAULT_MIN_POOL_SIZE = 10
DEFAULT_MAX_IDLE_TIME_MS = 30000
DEFAULT_RETRY_WRITES = True
DEFAULT_RETRY_READS = True
DEFAULT_WRITE_CONCERN = "majority"

# Default connection options
DEFAULT_CONNECTION_OPTIONS: Dict[str, Any] = {
    "maxPoolSize": DEFAULT_MAX_POOL_SIZE,
    "minPoolSize": DEFAULT_MIN_POOL_SIZE,
    "maxIdleTimeMS": DEFAULT_MAX_IDLE_TIME_MS,
    "connectTimeoutMS": DEFAULT_TIMEOUT_MS,
    "socketTimeoutMS": DEFAULT_TIMEOUT_MS,
    "serverSelectionTimeoutMS": DEFAULT_TIMEOUT_MS,
    "retryWrites": DEFAULT_RETRY_WRITES,
    "retryReads": DEFAULT_RETRY_READS,
    "w": DEFAULT_WRITE_CONCERN,
}

# Default index options
DEFAULT_INDEX_OPTIONS: Dict[str, Any] = {
    "background": True,
}

# Log levels
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"
