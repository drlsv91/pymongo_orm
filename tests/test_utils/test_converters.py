"""
Tests for utility converter functions.
"""

import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, AsyncMock, patch

from mongomodel.utils.converters import (
    ensure_object_id,
    process_query,
    doc_to_model,
    model_to_doc,
    docs_to_models,
    format_timestamp,
)


class TestModel:
    """Test model class for converter functions."""

    id: str = None
    name: str = ""
    age: int = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def model_dump(self, exclude=None):
        """Simulate Pydantic's model_dump method."""
        exclude = exclude or set()
        return {k: v for k, v in self.__dict__.items() if k not in exclude}


class TestUtilConverters:
    """Tests for utility converter functions."""

    def test_ensure_object_id(self):
        """Test ObjectId conversion."""
        # Test with string ID
        id_str = "507f1f77bcf86cd799439011"
        obj_id = ensure_object_id(id_str)
        assert isinstance(obj_id, ObjectId)
        assert str(obj_id) == id_str

        # Test with existing ObjectId
        original_obj_id = ObjectId()
        converted_obj_id = ensure_object_id(original_obj_id)
        assert converted_obj_id is original_obj_id

        # Test with None
        assert ensure_object_id(None) is None

    def test_process_query(self):
        """Test query processing."""
        # Test with _id as string
        query = {"_id": "507f1f77bcf86cd799439011"}
        processed = process_query(query)
        assert isinstance(processed["_id"], ObjectId)

        # Test with id field
        query = {"id": "507f1f77bcf86cd799439011"}
        processed = process_query(query)
        assert "id" not in processed
        assert isinstance(processed["_id"], ObjectId)

        # Test with other fields
        query = {"name": "Test", "age": {"$gt": 30}}
        processed = process_query(query)
        assert processed == query

    def test_doc_to_model(self):
        """Test document to model conversion."""
        # Test with _id field
        doc = {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Test", "age": 30}
        model = doc_to_model(doc, TestModel)
        assert model.id == "507f1f77bcf86cd799439011"
        assert model.name == "Test"
        assert model.age == 30
        assert not hasattr(model, "_id")

        # Test without _id field
        doc = {"name": "Test", "age": 30}
        model = doc_to_model(doc, TestModel)
        assert model.id is None
        assert model.name == "Test"
        assert model.age == 30

    def test_model_to_doc(self):
        """Test model to document conversion."""
        # Test with id field
        model = TestModel(id="507f1f77bcf86cd799439011", name="Test", age=30)
        doc = model_to_doc(model)
        assert "_id" in doc
        assert isinstance(doc["_id"], ObjectId)
        assert "id" not in doc
        assert doc["name"] == "Test"
        assert doc["age"] == 30

        # Test with exclude_id=True
        doc = model_to_doc(model, exclude_id=True)
        assert "_id" not in doc
        assert "id" not in doc
        assert doc["name"] == "Test"
        assert doc["age"] == 30

        # Test without id field
        model = TestModel(name="Test", age=30)
        doc = model_to_doc(model)
        assert "_id" not in doc
        assert "id" not in doc
        assert doc["name"] == "Test"
        assert doc["age"] == 30

    def test_docs_to_models(self):
        """Test multiple documents to models conversion."""
        docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "Test1", "age": 30},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "Test2", "age": 40},
        ]
        models = docs_to_models(docs, TestModel)
        assert len(models) == 2
        assert models[0].id == "507f1f77bcf86cd799439011"
        assert models[0].name == "Test1"
        assert models[0].age == 30
        assert models[1].id == "507f1f77bcf86cd799439012"
        assert models[1].name == "Test2"
        assert models[1].age == 40

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        # Test with specific datetime
        dt = datetime(2023, 1, 1, 12, 0, 0)
        formatted = format_timestamp(dt)
        assert formatted == "2023-01-01T12:00:00"

        # Test without datetime (defaults to now)
        formatted = format_timestamp()
        assert isinstance(formatted, str)
        # Basic validation - should be in ISO format
        assert "T" in formatted
        assert len(formatted) >= 19  # YYYY-MM-DDTHH:MM:SS
