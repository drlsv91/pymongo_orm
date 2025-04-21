"""
Test configuration and fixtures for PyMongo ORM.
"""

import mongomock_motor
from unittest.mock import AsyncMock, MagicMock
import pytest
import mongomock
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# pymongo_orm
from pymongo_orm.sync_model.connection import SyncMongoConnection
from pymongo_orm.async_model.connection import AsyncMongoConnection


# Fixtures for mock MongoDB connections
@pytest.fixture
def mock_motor_client():
    """
    Provide a mock Motor client for testing async operations.
    """
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    mock_db = MagicMock()
    mock_collection = MagicMock()

    # Setup the structure
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock the async methods
    mock_collection.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="mock_id")
    )
    mock_collection.find_one = AsyncMock()
    mock_collection.find = AsyncMock()
    mock_collection.update_one = AsyncMock()
    mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    mock_collection.delete_many = AsyncMock(return_value=MagicMock(deleted_count=1))
    mock_collection.update_many = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_collection.count_documents = AsyncMock(return_value=1)
    mock_collection.create_indexes = AsyncMock()
    mock_collection.aggregate = AsyncMock()
    mock_collection.bulk_write = AsyncMock()

    return mock_client


@pytest.fixture
def mock_pymongo_client():
    """
    Provide a mock PyMongo client for testing sync operations.
    """
    return mongomock.MongoClient()


@pytest.fixture
def mock_motor_client():
    """
    Provide a mock Motor client for testing async operations.
    """
    return mongomock_motor.AsyncMongoMockClient()


# Fixtures for MongoDB connections using mocks
@pytest.fixture
def sync_connection(monkeypatch, mock_pymongo_client):
    """
    Create a sync connection using a mock PyMongo client.
    """
    # Patch the MongoClient class to return our mock client
    monkeypatch.setattr(
        MongoClient, "__new__", lambda cls, *args, **kwargs: mock_pymongo_client
    )

    # Create and return the connection
    conn = SyncMongoConnection("mongodb://localhost:27017")
    yield conn

    # Clean up
    SyncMongoConnection._instances.clear()


@pytest.fixture
def async_connection(monkeypatch, mock_motor_client):
    """
    Create an async connection using a mock Motor client.
    """
    # Patch the AsyncIOMotorClient class to return our mock client
    monkeypatch.setattr(
        AsyncIOMotorClient, "__new__", lambda cls, *args, **kwargs: mock_motor_client
    )

    # Create and return the connection
    conn = AsyncMongoConnection("mongodb://localhost:27017")
    yield conn

    # Clean up
    AsyncMongoConnection._instances.clear()


# Database fixtures
@pytest.fixture
def sync_db(sync_connection):
    """
    Provide a sync database for testing.
    """
    return sync_connection.get_db(db_name="test_db")


@pytest.fixture
def async_db(async_connection):
    """
    Provide an async database for testing.
    """
    return async_connection.get_db(db_name="test_db")


# Test model fixtures
@pytest.fixture
def test_data():
    """
    Provide test data for models.
    """
    return {
        "users": [
            {"name": "User 1", "email": "user1@example.com", "age": 25},
            {"name": "User 2", "email": "user2@example.com", "age": 30},
            {"name": "User 3", "email": "user3@example.com", "age": 35},
        ],
    }
