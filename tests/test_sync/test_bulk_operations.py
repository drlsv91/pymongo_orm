"""
Tests for bulk operations in synchronous MongoDB model.
"""

import pytest
from pymongo import InsertOne, UpdateOne, DeleteOne, ASCENDING
from bson import ObjectId

from mongomodel.sync_model.model import SyncMongoModel


class TestUser(SyncMongoModel):
    """Test user model for synchronous operations."""

    __collection__ = "users"
    __indexes__ = [{"fields": [("email", ASCENDING)], "unique": True}]

    name: str
    email: str
    age: int


class TestBulkOperations:
    """Tests for bulk operations."""

    def test_bulk_write(self, sync_db, test_data, monkeypatch):
        """Test bulk_write operation."""
        # Mock the bulk_write method of collection
        bulk_result = type(
            "BulkWriteResult",
            (),
            {
                "bulk_api_result": {"nInserted": 2, "nModified": 1, "nRemoved": 1},
                "inserted_count": 2,
                "modified_count": 1,
                "deleted_count": 1,
            },
        )

        # Define a mock collection with bulk_write method
        collection_mock = sync_db[TestUser.__collection__]

        # Store the original method before patching
        original_bulk_write = collection_mock.bulk_write

        # Define the mock function
        def mock_bulk_write(operations, ordered=None):
            # Verify operations
            assert len(operations) == 4

            # Verify operation types
            assert isinstance(operations[0], InsertOne)
            assert isinstance(operations[1], InsertOne)
            assert isinstance(operations[2], UpdateOne)
            assert isinstance(operations[3], DeleteOne)

            # Verify operation contents
            assert operations[0]._doc["name"] == "User 1"
            assert operations[1]._doc["name"] == "User 2"
            assert operations[2]._filter["email"] == "user3@example.com"
            # assert "$set" in operations[2]._upsert
            # assert operations[2]._upsert["$set"]["age"] == 35
            assert operations[3]._filter["email"] == "user4@example.com"

            return bulk_result

        # Patch the bulk_write method
        monkeypatch.setattr(collection_mock, "bulk_write", mock_bulk_write)

        # Create bulk operations
        operations = [
            InsertOne({"name": "User 1", "email": "user1@example.com", "age": 25}),
            InsertOne({"name": "User 2", "email": "user2@example.com", "age": 30}),
            UpdateOne({"email": "user3@example.com"}, {"$set": {"age": 35}}),
            DeleteOne({"email": "user4@example.com"}),
        ]

        # Execute bulk operations
        result = TestUser.bulk_write(sync_db, operations)

        # Verify results
        assert result.inserted_count == 2
        assert result.modified_count == 1
        assert result.deleted_count == 1

        # Restore original method
        monkeypatch.setattr(collection_mock, "bulk_write", original_bulk_write)

    def test_bulk_insert(self, sync_db, test_data, monkeypatch):
        """Test bulk insert using bulk_write."""
        # First, create several test users
        users_data = [
            {"name": "Bulk User 1", "email": "bulk1@example.com", "age": 25},
            {"name": "Bulk User 2", "email": "bulk2@example.com", "age": 30},
            {"name": "Bulk User 3", "email": "bulk3@example.com", "age": 35},
        ]

        # Create bulk operations for inserting users
        operations = [InsertOne(user_data) for user_data in users_data]

        # Mock the bulk_write method
        collection_mock = sync_db[TestUser.__collection__]

        bulk_result = type(
            "BulkWriteResult",
            (),
            {"inserted_count": 3, "modified_count": 0, "deleted_count": 0},
        )

        # Store the original method before patching
        original_bulk_write = collection_mock.bulk_write

        # Define the mock function
        def mock_bulk_write(ops, ordered=None):
            # Verify operations
            assert len(ops) == 3
            assert all(isinstance(op, InsertOne) for op in ops)
            return bulk_result

        # Patch the bulk_write method
        monkeypatch.setattr(collection_mock, "bulk_write", mock_bulk_write)

        # Execute bulk operations
        result = TestUser.bulk_write(sync_db, operations)

        # Verify results
        assert result.inserted_count == 3
        assert result.modified_count == 0
        assert result.deleted_count == 0

        # Restore original method
        monkeypatch.setattr(collection_mock, "bulk_write", original_bulk_write)

    def test_bulk_update(self, sync_db, test_data, monkeypatch):
        """Test bulk update using bulk_write."""
        # Create bulk operations for updating users
        operations = [
            UpdateOne({"email": "user1@example.com"}, {"$set": {"age": 26}}),
            UpdateOne({"email": "user2@example.com"}, {"$set": {"age": 31}}),
            UpdateOne({"email": "user3@example.com"}, {"$set": {"age": 36}}),
        ]

        # Mock the bulk_write method
        collection_mock = sync_db[TestUser.__collection__]

        bulk_result = type(
            "BulkWriteResult",
            (),
            {"inserted_count": 0, "modified_count": 3, "deleted_count": 0},
        )

        # Store the original method before patching
        original_bulk_write = collection_mock.bulk_write

        # Define the mock function
        def mock_bulk_write(ops, ordered=None):
            # Verify operations
            assert len(ops) == 3
            assert all(isinstance(op, UpdateOne) for op in ops)
            return bulk_result

        # Patch the bulk_write method
        monkeypatch.setattr(collection_mock, "bulk_write", mock_bulk_write)

        # Execute bulk operations
        result = TestUser.bulk_write(sync_db, operations)

        # Verify results
        assert result.inserted_count == 0
        assert result.modified_count == 3
        assert result.deleted_count == 0

        # Restore original method
        monkeypatch.setattr(collection_mock, "bulk_write", original_bulk_write)

    def test_bulk_delete(self, sync_db, test_data, monkeypatch):
        """Test bulk delete using bulk_write."""
        # Create bulk operations for deleting users
        operations = [
            DeleteOne({"email": "user1@example.com"}),
            DeleteOne({"email": "user2@example.com"}),
            DeleteOne({"email": "user3@example.com"}),
        ]

        # Mock the bulk_write method
        collection_mock = sync_db[TestUser.__collection__]

        bulk_result = type(
            "BulkWriteResult",
            (),
            {"inserted_count": 0, "modified_count": 0, "deleted_count": 3},
        )

        # Store the original method before patching
        original_bulk_write = collection_mock.bulk_write

        # Define the mock function
        def mock_bulk_write(ops, ordered=None):
            # Verify operations
            assert len(ops) == 3
            assert all(isinstance(op, DeleteOne) for op in ops)
            return bulk_result

        # Patch the bulk_write method
        monkeypatch.setattr(collection_mock, "bulk_write", mock_bulk_write)

        # Execute bulk operations
        result = TestUser.bulk_write(sync_db, operations)

        # Verify results
        assert result.inserted_count == 0
        assert result.modified_count == 0
        assert result.deleted_count == 3

        # Restore original method
        monkeypatch.setattr(collection_mock, "bulk_write", original_bulk_write)
