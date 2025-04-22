"""
Asynchronous MongoDB model implementation.
"""

import inspect
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from ..abstract.implementation import AbstractMongoImplementation
from ..abstract.model import AbstractMongoModel
from ..utils.logging import get_logger
from .implementation import AsyncMongoImplementation

# Type variables
T = TypeVar("T", bound="AsyncMongoModel")
QueryType = Dict[str, Any]
ProjectionType = Dict[str, Any]
SortType = List[tuple]

logger = get_logger("async.model")


class AsyncMongoModel(AbstractMongoModel[AsyncIOMotorDatabase, AsyncIOMotorCollection]):
    """
    Base class for asynchronous MongoDB models.

    This class implements the abstract methods from AbstractMongoModel using
    the asynchronous implementation.
    """

    async def save(self, db: AsyncIOMotorDatabase) -> T:
        """
        Save the model to the database.

        Args:
            db: Database instance

        Returns:
            Saved model instance
        """
        return await AsyncMongoImplementation.save(self, db)

    @classmethod
    async def find_one(
        cls: Type[T],
        db: AsyncIOMotorDatabase,
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
        return await AsyncMongoImplementation.find_one(cls, db, query, projection)

    @classmethod
    async def find(
        cls: Type[T],
        db: AsyncIOMotorDatabase,
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
        return await AsyncMongoImplementation.find(
            cls,
            db,
            query,
            projection,
            sort,
            skip,
            limit,
        )

    async def delete(self, db: AsyncIOMotorDatabase) -> bool:
        """
        Delete this document from the database.

        Args:
            db: Database instance

        Returns:
            True if deleted, False otherwise
        """
        return await AsyncMongoImplementation.delete(self, db)

    @classmethod
    async def delete_many(cls, db: AsyncIOMotorDatabase, query: QueryType) -> int:
        """
        Delete multiple documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query

        Returns:
            Number of documents deleted
        """
        return await AsyncMongoImplementation.delete_many(cls, db, query)

    @classmethod
    async def update_many(
        cls,
        db: AsyncIOMotorDatabase,
        query: QueryType,
        update: Dict[str, Any],
    ) -> int:
        """
        Update multiple documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query
            update: Update specification

        Returns:
            Number of documents updated
        """
        return await AsyncMongoImplementation.update_many(cls, db, query, update)

    @classmethod
    async def count(
        cls,
        db: AsyncIOMotorDatabase,
        query: Optional[QueryType] = None,
    ) -> int:
        """
        Count documents matching the query.

        Args:
            db: Database instance
            query: MongoDB query

        Returns:
            Document count
        """
        return await AsyncMongoImplementation.count(cls, db, query)

    @classmethod
    async def ensure_indexes(cls, db: AsyncIOMotorDatabase) -> None:
        """
        Create indexes for this collection.

        Args:
            db: Database instance
        """
        await AsyncMongoImplementation.ensure_indexes(cls, db)

    @classmethod
    async def aggregate(
        cls,
        db: AsyncIOMotorDatabase,
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
        return await AsyncMongoImplementation.aggregate(cls, db, pipeline)

    @classmethod
    async def bulk_write(
        cls,
        db: AsyncIOMotorDatabase,
        operations: List[Dict[str, Any]],
    ) -> Any:
        """
        Execute multiple write operations.

        Args:
            db: Database instance
            operations: Write operations

        Returns:
            Bulk write result
        """
        return await AsyncMongoImplementation.bulk_write(cls, db, operations)

    @classmethod
    def get_mongo_implementation(cls) -> Type[AbstractMongoImplementation]:
        """
        Get the MongoDB implementation for this model.

        Returns:
            MongoDB implementation
        """
        return AsyncMongoImplementation

    async def _run_hooks(self, hooks: List[Callable]) -> None:
        """Run hooks, properly handling async hooks."""
        for hook in hooks:
            result = hook(self)
            if inspect.iscoroutine(result):
                await result

    async def _prepare_for_save(self) -> None:
        """Prepare the model for saving."""
        self.updated_at = datetime.now(timezone.utc)
        await self._run_hooks(self._pre_save_hooks)
