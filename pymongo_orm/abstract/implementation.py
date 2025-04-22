"""
Abstract MongoDB implementation interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

# Type variables
T = TypeVar("T")
D = TypeVar("D")  # Database type
QueryType = Dict[str, Any]
ProjectionType = Dict[str, Any]
SortType = List[Tuple[str, int]]


class AbstractMongoImplementation(ABC):
    """
    Abstract base class defining the interface for MongoDB operations.

    This class defines the standard operations that both sync and async
    implementations must provide.
    """

    @classmethod
    @abstractmethod
    def save(cls, model: Any, db: D) -> Any:
        """
        Save a model to the database.

        Args:
            model: Model instance to save
            db: Database instance

        Returns:
            The saved model instance
        """

    @classmethod
    @abstractmethod
    def find_one(
        cls,
        model_class: Type[T],
        db: D,
        query: QueryType,
        projection: Optional[ProjectionType] = None,
    ) -> Optional[T]:
        """
        Find a single document matching the query.

        Args:
            model_class: Model class
            db: Database instance
            query: MongoDB query
            projection: Fields to include/exclude

        Returns:
            Model instance or None if not found
        """

    @classmethod
    @abstractmethod
    def find(
        cls,
        model_class: Type[T],
        db: D,
        query: Optional[QueryType] = None,
        projection: Optional[ProjectionType] = None,
        sort: Optional[SortType] = None,
        skip: int = 0,
        limit: int = 0,
    ) -> List[T]:
        """
        Find documents matching the query.

        Args:
            model_class: Model class
            db: Database instance
            query: MongoDB query
            projection: Fields to include/exclude
            sort: Sort specification
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of model instances
        """

    @classmethod
    @abstractmethod
    def delete(cls, model: Any, db: D) -> bool:
        """
        Delete a model from the database.

        Args:
            model: Model instance to delete
            db: Database instance

        Returns:
            True if deleted, False otherwise
        """

    @classmethod
    @abstractmethod
    def delete_many(cls, model_class: Type[T], db: D, query: QueryType) -> int:
        """
        Delete multiple documents matching the query.

        Args:
            model_class: Model class
            db: Database instance
            query: MongoDB query

        Returns:
            Number of documents deleted
        """

    @classmethod
    @abstractmethod
    def update_many(
        cls,
        model_class: Type[T],
        db: D,
        query: QueryType,
        update: Dict[str, Any],
    ) -> int:
        """
        Update multiple documents matching the query.

        Args:
            model_class: Model class
            db: Database instance
            query: MongoDB query
            update: Update specification

        Returns:
            Number of documents updated
        """

    @classmethod
    @abstractmethod
    def count(
        cls,
        model_class: Type[T],
        db: D,
        query: Optional[QueryType] = None,
    ) -> int:
        """
        Count documents matching the query.

        Args:
            model_class: Model class
            db: Database instance
            query: MongoDB query

        Returns:
            Document count
        """

    @classmethod
    @abstractmethod
    def ensure_indexes(cls, model_class: Type[T], db: D) -> None:
        """
        Create indexes for the model collection.

        Args:
            model_class: Model class
            db: Database instance
        """

    @classmethod
    @abstractmethod
    def aggregate(
        cls,
        model_class: Type[T],
        db: D,
        pipeline: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Run an aggregation pipeline.

        Args:
            model_class: Model class
            db: Database instance
            pipeline: Aggregation pipeline

        Returns:
            Pipeline results
        """

    @classmethod
    @abstractmethod
    def bulk_write(
        cls,
        model_class: Type[T],
        db: D,
        operations: List[Dict[str, Any]],
    ) -> Any:
        """
        Execute multiple write operations.

        Args:
            model_class: Model class
            db: Database instance
            operations: Write operations

        Returns:
            Bulk write result
        """
