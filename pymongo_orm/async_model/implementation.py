"""
Asynchronous MongoDB implementation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..abstract.implementation import AbstractMongoImplementation
from ..exceptions import IndexError, MongoORMError, QueryError
from ..utils.converters import doc_to_model, ensure_object_id, process_query
from ..utils.decorators import async_timing_decorator
from ..utils.logging import get_logger

# Type variables
T = TypeVar("T")
QueryType = Dict[str, Any]
ProjectionType = Dict[str, Any]

logger = get_logger("async_model.implementation")


class AsyncMongoImplementation(AbstractMongoImplementation):
    """Asynchronous MongoDB implementation using Motor."""

    @classmethod
    @async_timing_decorator
    async def save(cls, model: Any, db: AsyncIOMotorDatabase) -> Any:
        """
        Save a model to the database.

        Args:
            model: Model instance to save
            db: Database instance

        Returns:
            The saved model instance
        """
        # Prepare model and get data
        await model._prepare_for_save()
        collection = model.get_collection(db)
        model_data = model.model_dump(exclude={"id"})

        try:
            if model.id is None:
                # Insert new document
                result = await collection.insert_one(model_data)
                model.id = str(result.inserted_id)
                logger.debug(f"Created document with id: {model.id}")
            else:
                # Update existing document
                result = await collection.update_one(
                    {"_id": ensure_object_id(model.id)},
                    {"$set": model_data},
                )
                if result.matched_count == 0:
                    logger.warning(f"No document found with id: {model.id}")
                logger.debug(f"Updated document with id: {model.id}")

            # Run post-save hooks
            await model._run_hooks(model._post_save_hooks)
            return model
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error during save: {e}")
            raise MongoORMError(f"Failed to save document: {e}")

    @classmethod
    @async_timing_decorator
    async def find_one(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
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
        collection = model_class.get_collection(db)
        processed_query = process_query(query)

        try:
            doc = await collection.find_one(processed_query, projection)
            if doc:

                return doc_to_model(doc, model_class)
            return None
        except PyMongoError as e:
            logger.error(f"MongoDB error during find_one: {e}")
            raise QueryError(
                collection=collection.name,
                query=processed_query,
                message=str(e),
            )

    @classmethod
    @async_timing_decorator
    async def find(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
        query: Optional[QueryType] = None,
        projection: Optional[ProjectionType] = None,
        sort: Optional[List[tuple]] = None,
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
        if query is None:
            query = {}

        collection = model_class.get_collection(db)
        processed_query = process_query(query)

        try:
            cursor = collection.find(processed_query, projection)

            # Apply sorting, skip, and limit
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)

            results = []
            async for doc in cursor:

                results.append(doc_to_model(doc, model_class))
            return results
        except PyMongoError as e:
            logger.error(f"MongoDB error during find: {e}")
            raise QueryError(
                collection=collection.name,
                query=processed_query,
                message=str(e),
            )

    @classmethod
    @async_timing_decorator
    async def delete(cls, model: Any, db: AsyncIOMotorDatabase) -> bool:
        """
        Delete a model from the database.

        Args:
            model: Model instance to delete
            db: Database instance

        Returns:
            True if deleted, False otherwise
        """
        if model.id is None:
            return False

        try:
            # Run pre-delete hooks
            await model._run_hooks(model._pre_delete_hooks)

            collection = model.get_collection(db)
            result = await collection.delete_one({"_id": ensure_object_id(model.id)})

            # Run post-delete hooks if deletion was successful
            if result.deleted_count > 0:
                await model._run_hooks(model._post_delete_hooks)
                logger.debug(f"Deleted document with id: {model.id}")
                return True

            logger.warning(f"Document with id {model.id} not found for deletion")
            return False
        except PyMongoError as e:
            logger.error(f"MongoDB error during delete: {e}")
            raise MongoORMError(f"Failed to delete document: {e}")

    @classmethod
    @async_timing_decorator
    async def delete_many(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
        query: QueryType,
    ) -> int:
        """
        Delete multiple documents matching the query.

        Args:
            model_class: Model class
            db: Database instance
            query: MongoDB query

        Returns:
            Number of documents deleted
        """
        collection = model_class.get_collection(db)
        processed_query = process_query(query)

        try:
            result = await collection.delete_many(processed_query)
            logger.debug(f"Deleted {result.deleted_count} documents")
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"MongoDB error during delete_many: {e}")
            raise QueryError(
                collection=collection.name,
                query=processed_query,
                message=str(e),
            )

    @classmethod
    @async_timing_decorator
    async def update_many(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
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
        collection = model_class.get_collection(db)
        processed_query = process_query(query)

        # Ensure update has proper MongoDB format with $set, $unset, etc.
        if not any(key.startswith("$") for key in update):
            update = {"$set": update}

        # Add updated_at timestamp
        if "$set" in update:
            update["$set"]["updated_at"] = datetime.now(timezone.utc)
        else:
            update["$set"] = {"updated_at": datetime.now(timezone.utc)}

        try:
            result = await collection.update_many(processed_query, update)
            logger.debug(f"Updated {result.modified_count} documents")
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"MongoDB error during update_many: {e}")
            raise QueryError(
                collection=collection.name,
                query=processed_query,
                message=str(e),
            )

    @classmethod
    @async_timing_decorator
    async def count(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
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
        if query is None:
            query = {}

        collection = model_class.get_collection(db)
        processed_query = process_query(query)

        try:
            count = await collection.count_documents(processed_query)
            return count
        except PyMongoError as e:
            logger.error(f"MongoDB error during count: {e}")
            raise QueryError(
                collection=collection.name,
                query=processed_query,
                message=str(e),
            )

    @classmethod
    @async_timing_decorator
    async def ensure_indexes(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
    ) -> None:
        """
        Create indexes for the model collection.

        Args:
            model_class: Model class
            db: Database instance
        """
        collection = model_class.get_collection(db)
        index_configs = getattr(model_class, "__indexes__", [])

        try:
            # Create multiple indexes at once for better performance
            index_models = []

            for index_config in index_configs:
                fields = index_config.get("fields", [])
                kwargs = {k: v for k, v in index_config.items() if k != "fields"}

                # Process field specifications
                processed_fields = []
                for field_spec in fields:
                    if isinstance(field_spec, tuple):
                        processed_fields.append(field_spec)
                    else:
                        processed_fields.append((field_spec, 1))  # Default to ascending

                # Create index model
                index_models.append(IndexModel(processed_fields, **kwargs))

            if index_models:
                await collection.create_indexes(index_models)
                logger.info(
                    f"Created {len(index_models)} indexes for {model_class.__name__}",
                )
        except PyMongoError as e:
            logger.error(f"Error creating indexes: {e}")
            raise IndexError(
                collection=collection.name,
                index="multiple",
                message=str(e),
            )

    @classmethod
    @async_timing_decorator
    async def aggregate(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
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
        collection = model_class.get_collection(db)

        try:
            result = []
            cursor = collection.aggregate(pipeline)
            async for doc in cursor:
                # Convert ObjectId to string for _id
                if "_id" in doc and isinstance(doc["_id"], ObjectId):
                    doc["id"] = str(doc.pop("_id"))
                result.append(doc)
            return result
        except PyMongoError as e:
            logger.error(f"MongoDB error during aggregate: {e}")
            raise MongoORMError(f"Aggregation pipeline error: {e}")

    @classmethod
    @async_timing_decorator
    async def bulk_write(
        cls,
        model_class: Type[T],
        db: AsyncIOMotorDatabase,
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
        collection = model_class.get_collection(db)

        try:
            result = await collection.bulk_write(operations)
            return result
        except PyMongoError as e:
            logger.error(f"MongoDB error during bulk_write: {e}")
            raise MongoORMError(f"Bulk write error: {e}")
