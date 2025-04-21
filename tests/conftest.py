"""
Test configuration and fixtures for PyMongo ORM.
"""

import asyncio
import pytest
import mongomock
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# mongomodel
from mongomodel.sync_model.connection import SyncMongoConnection
from mongomodel.async_model.connection import AsyncMongoConnection


# @pytest.fixture(scope="session")
# def event_loop():
#     """
#     Create an instance of the default event loop for each test session.
#     """
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# Fixtures for mock MongoDB connections
@pytest.fixture
def mock_pymongo_client():
    """
    Provide a mock PyMongo client for testing sync operations.
    """
    return mongomock.MongoClient()


@pytest.fixture
def mock_motor_client(mock_pymongo_client):
    """
    Provide a mock Motor client for testing async operations.
    """
    return AsyncIOMotorClient(delegate=mock_pymongo_client)


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
