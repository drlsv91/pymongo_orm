"""
Synchronous MongoDB model implementation.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from pymongo.collection import Collection
from pymongo.database import Database

from ..abstract.implementation import AbstractMongoImplementation
from ..abstract.model import AbstractMongoModel
from ..utils.logging import get_logger
from .implementation import SyncMongoImplementation

# Type variables
T = TypeVar("T", bound="SyncMongoModel")
QueryType = Dict[str, Any]
ProjectionType = Dict[str, Any]
SortType = List[tuple]

logger = get_logger("sync.model")


class SyncMongoModel(AbstractMongoModel[Database, Collection]):
    """
    Base class for synchronous MongoDB models.

    This class implements the abstract methods from AbstractMongoModel using
    the synchronous implementation.
    """

    def save(self, db: Database) -> T:
        """
        Save the model to the database.

        Args:
            db: Database instance

        Returns:
            Saved model instance
        """
        return SyncMongoImplementation.save(self, db)

    @classmethod
    def find_one(
        cls: Type[T],
        db: Database,
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
        return SyncMongoImplementation.find_one(cls, db, query, projection)

    @classmethod
    def find(
        cls: Type[T],
        db: Database,
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
        return SyncMongoImplementation.find(
            cls,
            db,
            query,
            projection,
            sort,
            skip,
            limit,
        )

    def delete(self, db: Database) -> bool:
        """
        Delete this document from the database.

        Args:
            db: Database instance

        Returns:
            True if deleted, False otherwise
        """
        return SyncMongoImplementation.delete(self, db)

    @classmethod
    def delete_many(cls, db: Database, query: QueryType) -> int:
        """
        Delete multiple documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query

        Returns:
            Number of documents deleted
        """
        return SyncMongoImplementation.delete_many(cls, db, query)

    @classmethod
    def update_many(cls, db: Database, query: QueryType, update: Dict[str, Any]) -> int:
        """
        Update multiple documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query
            update: Update specification

        Returns:
            Number of documents updated
        """
        return SyncMongoImplementation.update_many(cls, db, query, update)

    @classmethod
    def count(cls, db: Database, query: Optional[QueryType] = None) -> int:
        """
        Count documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query

        Returns:
            Document count
        """
        return SyncMongoImplementation.count(cls, db, query)

    @classmethod
    def ensure_indexes(cls, db: Database) -> None:
        """
        Create indexes for this collection.

        Args:
            db: Database instance
        """
        SyncMongoImplementation.ensure_indexes(cls, db)

    @classmethod
    def aggregate(
        cls,
        db: Database,
        pipeline: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Run an aggregation pipeline.

        Args:
            db: Database instance
            pipeline: Aggregation pipeline

        Returns:
            Pipeline results
        """
        return SyncMongoImplementation.aggregate(cls, db, pipeline)

    @classmethod
    def bulk_write(cls, db: Database, operations: List[Dict[str, Any]]) -> Any:
        """
        Execute multiple write operations.

        Args:
            db: Database instance
            operations: Write operations

        Returns:
            Bulk write result
        """
        return SyncMongoImplementation.bulk_write(cls, db, operations)

    @classmethod
    def get_mongo_implementation(cls) -> Type[AbstractMongoImplementation]:
        """
        Get the MongoDB implementation for this model.

        Returns:
            MongoDB implementation
        """
        return SyncMongoImplementation
