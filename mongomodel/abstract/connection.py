"""
Abstract connection class for MongoDB.
"""

from abc import ABC, abstractmethod
import threading
from typing import Any, Dict, ClassVar


class AbstractMongoConnection(ABC):
    """
    Abstract base class for MongoDB connections.

    This class implements the singleton pattern to ensure only one connection
    is created for each URI.
    """

    _instances: ClassVar[Dict[str, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @abstractmethod
    def __new__(cls, uri: str, **kwargs: Any) -> "AbstractMongoConnection":
        """
        Create a new connection or return an existing one.

        Args:
            uri: MongoDB connection URI
            **kwargs: Additional connection options

        Returns:
            Connection instance
        """
        pass

    @abstractmethod
    def get_db(self, *, db_name: str) -> Any:
        """
        Get a database from the connection.

        Args:
            db_name: Database name

        Returns:
            Database instance
        """
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """
        Get the underlying MongoDB client.

        Returns:
            MongoDB client instance
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the MongoDB connection and clean up resources.
        """
        pass
