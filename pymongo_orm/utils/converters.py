"""
Type conversion utilities for MongoDB ORM.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from bson import ObjectId

# Type aliases
Document = Dict[str, Any]
Query = Dict[str, Any]
T = TypeVar("T")


def resolve_collection_name(cls: Type[T]) -> str:
    """Determine the appropriate collection name for this model class."""
    # Check for explicit collection name override
    if hasattr(cls, "__collection__"):
        collection_name = cls.__collection__
        if not isinstance(collection_name, str) or not collection_name.strip():
            raise ValueError(
                f"__collection__ must be a non-empty string. Got: {collection_name}",
            )
        return collection_name

    # Default to lowercase pluralized class name
    class_name = cls.__name__.lower()
    if not class_name.endswith("s"):
        class_name += "s"

    return class_name


def ensure_object_id(id_value: Union[str, ObjectId, None]) -> Optional[ObjectId]:
    """
    Convert string ID to ObjectId.

    Args:
        id_value: ID value as string or ObjectId

    Returns:
        ObjectId instance or None
    """
    if id_value is None:
        return None
    if isinstance(id_value, ObjectId):
        return id_value
    return ObjectId(id_value)


def process_query(query: Query) -> Query:
    """
    Process a query dict to convert string IDs to ObjectIds.

    Args:
        query: MongoDB query dictionary

    Returns:
        Processed query with ObjectIds
    """
    processed_query = query.copy()

    # Handle ObjectId conversion for _id
    if "_id" in processed_query and isinstance(processed_query["_id"], str):
        processed_query["_id"] = ensure_object_id(processed_query["_id"])
    elif "id" in processed_query:
        id_value = processed_query.pop("id")
        processed_query["_id"] = ensure_object_id(id_value)

    return processed_query


def doc_to_model(doc: Document, model_class: Type[T]) -> T:
    """
    Convert MongoDB document to model instance.

    Args:
        doc: MongoDB document
        model_class: Model class to instantiate

    Returns:
        Model instance
    """
    doc_copy = doc.copy()

    # Convert _id to id
    if "_id" in doc_copy:
        doc_copy["id"] = str(doc_copy.pop("_id"))

    return model_class(**doc_copy)


def model_to_doc(model: Any, exclude_id: bool = False) -> Document:
    """
    Convert model instance to MongoDB document.

    Args:
        model: Model instance
        exclude_id: Whether to exclude the ID field

    Returns:
        MongoDB document
    """
    exclude = {"id"} if exclude_id else set()
    doc: Document = model.model_dump(exclude=exclude)

    # Convert id to _id if present and not excluded
    if not exclude_id and "id" in doc and doc["id"] is not None:
        doc["_id"] = ensure_object_id(doc.pop("id"))

    return doc


def docs_to_models(docs: List[Document], model_class: Type[T]) -> List[T]:
    """
    Convert a list of MongoDB documents to model instances.

    Args:
        docs: List of MongoDB documents
        model_class: Model class to instantiate

    Returns:
        List of model instances
    """
    return [doc_to_model(doc, model_class) for doc in docs]


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime object as ISO string.

    Args:
        dt: Datetime object (defaults to current time)

    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()
