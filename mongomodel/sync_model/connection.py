"""
Synchronous MongoDB connection implementation.
"""

import threading
from typing import Any, Dict

from pymongo import MongoClient
from pymongo.database import Database

from ..abstract.connection import AbstractMongoConnection
from ..config import DEFAULT_CONNECTION_OPTIONS
from ..utils.logging import get_logger

logger = get_logger("sync.connection")


class SyncMongoConnection(AbstractMongoConnection):
    """
    Synchronous MongoDB connection using PyMongo.

    This class implements the singleton pattern to ensure only one connection
    is created for each URI.
    """

    _instances: Dict[str, "SyncMongoConnection"] = {}
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, uri: str, **kwargs: Any) -> "SyncMongoConnection":
        """
        Create a new connection or return an existing one.

        Args:
            uri: MongoDB connection URI
            **kwargs: Additional connection options

        Returns:
            Connection instance
        """

        with cls._lock:
            if uri not in cls._instances:

                instance = object.__new__(cls)
                connection_kwargs = {**DEFAULT_CONNECTION_OPTIONS, **kwargs}

                instance._client = MongoClient(uri, **connection_kwargs)
                logger.info(f"Created new SyncMongoConnection to {uri}")
                instance._uri = uri
                cls._instances[uri] = instance
            return cls._instances[uri]

    def get_db(self, *, db_name: str) -> Database:
        """
        Get a database from the connection.

        Args:
            db_name: Database name

        Returns:
            Database instance
        """
        return self._client[db_name]

    def get_client(self) -> MongoClient:
        """
        Get the underlying MongoDB client.

        Returns:
            MongoClient instance
        """
        return self._client

    def close(self) -> None:
        """
        Close the MongoDB connection and clean up resources.
        """
        if hasattr(self, "_client"):
            logger.info(f"Closing SyncMongoConnection to {self._uri}")
            self._client.close()
            with self._lock:
                if self._uri in self._instances:
                    del self._instances[self._uri]
