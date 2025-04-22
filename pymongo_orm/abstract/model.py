"""
Abstract model base class for MongoDB ORM.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, cast

from pydantic import BaseModel, Field

from ..utils.converters import resolve_collection_name
from .implementation import (
    AbstractMongoImplementation,
    ProjectionType,
    QueryType,
    SortType,
)

# Type variables
T = TypeVar("T", bound="AbstractMongoModel")
D = TypeVar("D")  # Database type
C = TypeVar("C")  # Collection type


class AbstractMongoModel(BaseModel, Generic[D, C], ABC):
    """
    Abstract base class for MongoDB models.

    This class provides the base structure and interface for MongoDB models
    in both synchronous and asynchronous contexts.
    """

    id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Hooks for custom logic
    _pre_save_hooks: List[Callable] = []
    _post_save_hooks: List[Callable] = []
    _pre_delete_hooks: List[Callable] = []
    _post_delete_hooks: List[Callable] = []

    # Collection configuration
    __collection__: str = ""
    __indexes__: List[Dict[str, Any]] = []
    __write_concern__: Dict[str, Any] = {"w": 1}
    __read_preference__: str = "primary"

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        validate_assignment = True

    @classmethod
    def get_collection(cls, db: D) -> C:
        """
        Get the MongoDB collection for this model.

        Args:
            db: Database instance

        Returns:
            Collection instance
        """

        collection_name = resolve_collection_name(cls)

        return cast(C, db[collection_name])

    @abstractmethod
    def save(self, db: D) -> T:
        """
        Save the model to the database.

        Args:
            db: Database instance

        Returns:
            Saved model instance
        """

    @classmethod
    @abstractmethod
    def find_one(
        cls: Type[T],
        db: D,
        query: QueryType,
        projection: Optional[ProjectionType] = None,
    ) -> Optional[T]:
        """
        Find a single document matching the query.

        Args:
            db: Database instance
            query: MongoDB query
            projection: Fields to include/exclude

        Returns:
            Model instance or None if not found
        """

    @classmethod
    @abstractmethod
    def find(
        cls: Type[T],
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
            db: Database instance
            query: MongoDB query
            projection: Fields to include/exclude
            sort: Sort specification
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of model instances
        """

    @abstractmethod
    def delete(self, db: D) -> bool:
        """
        Delete this document from the database.

        Args:
            db: Database instance

        Returns:
            True if deleted, False otherwise
        """

    @classmethod
    @abstractmethod
    def delete_many(cls, db: D, query: QueryType) -> int:
        """
        Delete multiple documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query

        Returns:
            Number of documents deleted
        """

    @classmethod
    @abstractmethod
    def update_many(cls, db: D, query: QueryType, update: Dict[str, Any]) -> int:
        """
        Update multiple documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query
            update: Update specification

        Returns:
            Number of documents updated
        """

    @classmethod
    @abstractmethod
    def count(cls, db: D, query: Optional[QueryType] = None) -> int:
        """
        Count documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query

        Returns:
            Document count
        """

    @classmethod
    @abstractmethod
    def ensure_indexes(cls, db: D) -> None:
        """
        Create indexes for this collection.

        Args:
            db: Database instance
        """

    @classmethod
    @abstractmethod
    def aggregate(cls, db: D, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run an aggregation pipeline.

        Args:
            db: Database instance
            pipeline: Aggregation pipeline

        Returns:
            Pipeline results
        """

    @classmethod
    @abstractmethod
    def bulk_write(cls, db: D, operations: List[Dict[str, Any]]) -> Any:
        """
        Execute multiple write operations.

        Args:
            db: Database instance
            operations: Write operations

        Returns:
            Bulk write result
        """

    @classmethod
    @abstractmethod
    def get_mongo_implementation(cls) -> AbstractMongoImplementation:
        """
        Get the MongoDB implementation for this model.

        Returns:
            MongoDB implementation
        """

    def _run_hooks(self, hooks: List[Callable]) -> None:
        """
        Run hooks on the model.

        Args:
            hooks: List of hook functions to run
        """
        for hook in hooks:
            hook(self)

    def _prepare_for_save(self) -> None:
        """
        Prepare the model for saving.

        This method updates the updated_at timestamp and runs pre-save hooks.
        """
        self.updated_at = datetime.now(timezone.utc)
        self._run_hooks(self._pre_save_hooks)
