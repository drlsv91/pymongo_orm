"""
Custom exceptions for MongoDB ORM.
"""

from typing import Any, Dict, Optional


class MongoORMError(Exception):
    """Base exception for all MongoDB ORM errors."""

    pass


class ConnectionError(MongoORMError):
    """Exception raised for connection errors."""

    def __init__(self, uri: str, message: str):
        self.uri = uri
        self.message = message
        super().__init__(f"Connection error for '{uri}': {message}")


class QueryError(MongoORMError):
    """Exception raised for query errors."""

    def __init__(self, collection: str, query: Dict[str, Any], message: str):
        self.collection = collection
        self.query = query
        self.message = message
        super().__init__(f"Query error for collection '{collection}': {message}")


class ValidationError(MongoORMError):
    """Exception raised for data validation errors."""

    def __init__(self, model: str, field: str, message: str):
        self.model = model
        self.field = field
        self.message = message
        super().__init__(f"Validation error for '{model}.{field}': {message}")


class IndexError(MongoORMError):
    """Exception raised for index creation errors."""

    def __init__(self, collection: str, index: str, message: str):
        self.collection = collection
        self.index = index
        self.message = message
        super().__init__(f"Index error for '{collection}.{index}': {message}")


class DocumentNotFoundError(MongoORMError):
    """Exception raised when a document is not found."""

    def __init__(self, collection: str, query: Dict[str, Any]):
        self.collection = collection
        self.query = query
        super().__init__(f"Document not found in '{collection}' for query: {query}")


class DuplicateKeyError(MongoORMError):
    """Exception raised for duplicate key errors."""

    def __init__(self, collection: str, key: str, value: Any):
        self.collection = collection
        self.key = key
        self.value = value
        super().__init__(f"Duplicate key '{key}={value}' in collection '{collection}'")


class TransactionError(MongoORMError):
    """Exception raised for transaction errors."""

    def __init__(self, message: str, transaction_id: Optional[str] = None):
        self.transaction_id = transaction_id
        self.message = message
        msg = f"Transaction error: {message}"
        if transaction_id:
            msg += f" (Transaction ID: {transaction_id})"
        super().__init__(msg)
