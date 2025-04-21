"""
Mongomodel ORM - A lightweight Object-Relational Mapping for MongoDB in Python.

This package provides a flexible and efficient way to work with MongoDB
in both synchronous and asynchronous contexts.
"""

from .utils.logging import setup_logging

# Setup default logging
logger = setup_logging()

from .abstract.model import AbstractMongoModel
from .async_model.model import AsyncMongoModel
from .async_model.connection import AsyncMongoConnection
from .sync_model.model import SyncMongoModel
from .sync_model.connection import SyncMongoConnection
from .exceptions import (
    MongoORMError,
    ConnectionError,
    QueryError,
    ValidationError,
    IndexError,
    DocumentNotFoundError,
    DuplicateKeyError,
)

__version__ = "0.1.0"
__author__ = "Oluwaleye Victor"
