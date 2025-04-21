"""
Tests for the MongoDB connection classes.
"""

from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

from mongomodel.sync_model.connection import SyncMongoConnection
from mongomodel.async_model.connection import AsyncMongoConnection


class TestConnections:
    """Tests for MongoDB connection classes."""

    def test_sync_connection_singleton(self, monkeypatch, mock_pymongo_client):
        """Test that SyncMongoConnection uses the singleton pattern."""
        # Patch the MongoClient class to return our mock client
        monkeypatch.setattr(
            MongoClient, "__new__", lambda cls, *args, **kwargs: mock_pymongo_client
        )

        # Create two connections with the same URI
        conn1 = SyncMongoConnection("mongodb://localhost:27017")
        conn2 = SyncMongoConnection("mongodb://localhost:27017")

        # They should be the same instance
        assert conn1 is conn2

        # Create a connection with a different URI
        conn3 = SyncMongoConnection("mongodb://localhost:27018")

        # It should be a different instance
        assert conn1 is not conn3

        # Clean up
        SyncMongoConnection._instances.clear()

    def test_async_connection_singleton(self, monkeypatch, mock_motor_client):
        """Test that AsyncMongoConnection uses the singleton pattern."""
        # Patch the AsyncIOMotorClient class to return our mock client
        monkeypatch.setattr(
            AsyncIOMotorClient,
            "__new__",
            lambda cls, *args, **kwargs: mock_motor_client,
        )

        # Create two connections with the same URI
        conn1 = AsyncMongoConnection("mongodb://localhost:27017")
        conn2 = AsyncMongoConnection("mongodb://localhost:27017")

        # They should be the same instance
        assert conn1 is conn2

        # Create a connection with a different URI
        conn3 = AsyncMongoConnection("mongodb://localhost:27018")

        # It should be a different instance
        assert conn1 is not conn3

        # Clean up
        AsyncMongoConnection._instances.clear()

    def test_sync_get_db(self, sync_connection):
        """Test getting a database from a sync connection."""
        # Get a database
        db = sync_connection.get_db(db_name="test_db")

        # Check that it's a database object
        assert db.name == "test_db"

    def test_async_get_db(self, async_connection):
        """Test getting a database from an async connection."""
        # Get a database
        db = async_connection.get_db(db_name="test_db")

        # Check that it's a database object
        assert db.name == "test_db"

    def test_sync_get_client(self, sync_connection, mock_pymongo_client):
        """Test getting the client from a sync connection."""
        # Get the client
        client = sync_connection.get_client()

        # Check that it's the mock client
        assert client is mock_pymongo_client

    def test_async_get_client(self, async_connection, mock_motor_client):
        """Test getting the client from an async connection."""
        # Get the client
        client = async_connection.get_client()

        # Check that it's the mock client
        assert client is mock_motor_client

    def test_sync_close(self, monkeypatch, mock_pymongo_client):
        """Test closing a sync connection."""
        # Track if close was called
        close_called = False

        # Mock the close method
        def mock_close():
            nonlocal close_called
            close_called = True

        mock_pymongo_client.close = mock_close

        # Patch the MongoClient class to return our mock client
        monkeypatch.setattr(
            MongoClient, "__new__", lambda cls, *args, **kwargs: mock_pymongo_client
        )

        # Create a connection
        conn = SyncMongoConnection("mongodb://localhost:27017")

        # Close it
        conn.close()

        # Check that close was called
        assert close_called is True

        # Check that the instance was removed
        assert "mongodb://localhost:27017" not in SyncMongoConnection._instances

        # Clean up
        SyncMongoConnection._instances.clear()

    def test_async_close(self, monkeypatch, mock_motor_client):
        """Test closing an async connection."""
        # Track if close was called
        close_called = False

        # Mock the close method
        def mock_close():
            nonlocal close_called
            close_called = True

        mock_motor_client.close = mock_close

        # Patch the AsyncIOMotorClient class to return our mock client
        monkeypatch.setattr(
            AsyncIOMotorClient,
            "__new__",
            lambda cls, *args, **kwargs: mock_motor_client,
        )

        # Create a connection
        conn = AsyncMongoConnection("mongodb://localhost:27017")

        # Close it
        conn.close()

        # Check that close was called
        assert close_called is True

        # Check that the instance was removed
        assert "mongodb://localhost:27017" not in AsyncMongoConnection._instances

        # Clean up
        AsyncMongoConnection._instances.clear()
