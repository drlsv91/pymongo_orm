"""
Mongomodel ORM - A lightweight Object-Relational Mapping for MongoDB in Python.

This package provides a flexible and efficient way to work with MongoDB
in both synchronous and asynchronous contexts.
"""

# First, all imports
from .abstract.model import AbstractMongoModel
from .async_model.connection import AsyncMongoConnection
from .async_model.model import AsyncMongoModel
from .exceptions import (
    ConnectionError,
    DocumentNotFoundError,
    DuplicateKeyError,
    IndexError,
    MongoORMError,
    QueryError,
    ValidationError,
)
from .sync_model.connection import SyncMongoConnection
from .sync_model.model import SyncMongoModel
from .utils.logging import setup_logging

# Then, executable code
# Setup default logging
logger = setup_logging()

# Module metadata
__version__ = "0.1.0"
__author__ = "Oluwaleye Victor"
