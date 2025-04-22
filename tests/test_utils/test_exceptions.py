"""
Tests for custom exception classes.
"""

from pymongo_orm.exceptions import (
    ConnectionError,
    DocumentNotFoundError,
    DuplicateKeyError,
    IndexError,
    MongoORMError,
    QueryError,
    TransactionError,
    ValidationError,
)


class TestExceptions:
    """Tests for custom exception classes."""

    def test_mongo_orm_error(self):
        """Test MongoORMError base exception."""
        error = MongoORMError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_connection_error(self):
        """Test ConnectionError exception."""
        uri = "mongodb://localhost:27017"
        message = "Failed to connect"
        error = ConnectionError(uri, message)

        assert error.uri == uri
        assert error.message == message
        assert "Connection error for 'mongodb://localhost:27017'" in str(error)
        assert "Failed to connect" in str(error)
        assert isinstance(error, MongoORMError)

    def test_query_error(self):
        """Test QueryError exception."""
        collection = "users"
        query = {"name": "Test"}
        message = "Invalid query"
        error = QueryError(collection, query, message)

        assert error.collection == collection
        assert error.query == query
        assert error.message == message
        assert "Query error for collection 'users'" in str(error)
        assert "Invalid query" in str(error)
        assert isinstance(error, MongoORMError)

    def test_validation_error(self):
        """Test ValidationError exception."""
        model = "User"
        field = "email"
        message = "Invalid email format"
        error = ValidationError(model, field, message)

        assert error.model == model
        assert error.field == field
        assert error.message == message
        assert "Validation error for 'User.email'" in str(error)
        assert "Invalid email format" in str(error)
        assert isinstance(error, MongoORMError)

    def test_index_error(self):
        """Test IndexError exception."""
        collection = "users"
        index = "email_idx"
        message = "Duplicate key error"
        error = IndexError(collection, index, message)

        assert error.collection == collection
        assert error.index == index
        assert error.message == message
        assert "Index error for 'users.email_idx'" in str(error)
        assert "Duplicate key error" in str(error)
        assert isinstance(error, MongoORMError)

    def test_document_not_found_error(self):
        """Test DocumentNotFoundError exception."""
        collection = "users"
        query = {"_id": "123"}
        error = DocumentNotFoundError(collection, query)

        assert error.collection == collection
        assert error.query == query
        assert "Document not found in 'users'" in str(error)
        assert "{'_id': '123'}" in str(error)
        assert isinstance(error, MongoORMError)

    def test_duplicate_key_error(self):
        """Test DuplicateKeyError exception."""
        collection = "users"
        key = "email"
        value = "test@example.com"
        error = DuplicateKeyError(collection, key, value)

        assert error.collection == collection
        assert error.key == key
        assert error.value == value
        assert "Duplicate key 'email=test@example.com'" in str(error)
        assert "in collection 'users'" in str(error)
        assert isinstance(error, MongoORMError)

    def test_transaction_error(self):
        """Test TransactionError exception."""
        message = "Transaction failed"
        error = TransactionError(message)

        assert error.message == message
        assert str(error) == "Transaction error: Transaction failed"
        assert isinstance(error, MongoORMError)

        # Test with transaction_id
        transaction_id = "abc123"
        error = TransactionError(message, transaction_id)

        assert error.transaction_id == transaction_id
        assert "Transaction ID: abc123" in str(error)
