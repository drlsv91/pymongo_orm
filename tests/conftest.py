"""
Test configuration and fixtures for PyMongo ORM.
"""

import mongomock
import mongomock_motor
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from pymongo_orm.async_model.connection import AsyncMongoConnection

# pymongo_orm
from pymongo_orm.sync_model.connection import SyncMongoConnection


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
        MongoClient,
        "__new__",
        lambda cls, *args, **kwargs: mock_pymongo_client,
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
        AsyncIOMotorClient,
        "__new__",
        lambda cls, *args, **kwargs: mock_motor_client,
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
