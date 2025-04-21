"""
Asynchronous MongoDB connection implementation.
"""

import threading
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..abstract.connection import AbstractMongoConnection
from ..config import DEFAULT_CONNECTION_OPTIONS
from ..utils.logging import get_logger

logger = get_logger("async.connection")


class AsyncMongoConnection(AbstractMongoConnection):
    """
    Asynchronous MongoDB connection using Motor.

    This class implements the singleton pattern to ensure only one connection
    is created for each URI.
    """

    _instances: Dict[str, "AsyncMongoConnection"] = {}
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, uri: str, **kwargs: Any) -> "AsyncMongoConnection":
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
                instance._client = AsyncIOMotorClient(uri, **connection_kwargs)
                instance._uri = uri
                cls._instances[uri] = instance
            return cls._instances[uri]

    def get_db(self, *, db_name: str) -> AsyncIOMotorDatabase:
        """
        Get a database from the connection.

        Args:
            db_name: Database name

        Returns:
            AsyncIOMotorDatabase instance
        """
        return self._client[db_name]

    def get_client(self) -> AsyncIOMotorClient:
        """
        Get the underlying MongoDB client.

        Returns:
            AsyncIOMotorClient instance
        """
        return self._client

    def close(self) -> None:
        """
        Close the MongoDB connection and clean up resources.
        """
        if hasattr(self, "_client"):
            logger.info(f"Closing AsyncMongoConnection to {self._uri}")
            self._client.close()
            with self._lock:
                if self._uri in self._instances:
                    del self._instances[self._uri]
