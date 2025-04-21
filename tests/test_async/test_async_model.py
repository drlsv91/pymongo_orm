"""
Tests for the asynchronous MongoDB model implementation.
"""

import pytest
from pymongo import ASCENDING

from pymongo_orm.async_model.model import AsyncMongoModel


class TestUser(AsyncMongoModel):
    """Test user model for asynchronous operations."""

    __collection__ = "users"
    __indexes__ = [{"fields": [("email", ASCENDING)], "unique": True}]

    name: str
    email: str
    age: int


class TestAsyncModel:
    """Tests for asynchronous MongoDB models."""

    @pytest.mark.asyncio
    async def test_create_and_save(self, async_db, test_data):
        """Test creating and saving a model."""
        # Create a new user
        user_data = test_data["users"][0]
        user = TestUser(**user_data)

        # Save the user
        saved_user = await user.save(async_db)

        # Check that the user was saved
        assert saved_user.id is not None
        assert saved_user.name == user_data["name"]
        assert saved_user.email == user_data["email"]
        assert saved_user.age == user_data["age"]

        # Find the user to confirm it was saved
        found_user = await TestUser.find_one(async_db, {"email": user_data["email"]})
        assert found_user is not None
        assert found_user.id == saved_user.id
        assert found_user.name == user_data["name"]

    @pytest.mark.asyncio
    async def test_find_and_query(self, async_db, test_data):
        """Test finding and querying models."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            await user.save(async_db)

        # Test find all
        all_users = await TestUser.find(async_db)
        assert len(all_users) == len(test_data["users"])

        # Test find with query
        users_over_30 = await TestUser.find(async_db, {"age": {"$gte": 30}})
        assert len(users_over_30) == 2
        assert all(user.age >= 30 for user in users_over_30)

        # Test find with projection
        users_with_projection = await TestUser.find(
            async_db, projection={"name": 1, "email": 1, "age": 1}
        )
        assert len(users_with_projection) == len(test_data["users"])
        assert hasattr(users_with_projection[0], "name")
        assert hasattr(users_with_projection[0], "email")
        # assert not hasattr(users_with_projection[0], "age")

        # Test find with sorting
        users_sorted = await TestUser.find(async_db, sort=[("age", -1)])
        assert users_sorted[0].age > users_sorted[-1].age

    @pytest.mark.asyncio
    async def test_update(self, async_db, test_data):
        """Test updating a model."""
        # Create and save a user
        user_data = test_data["users"][0]
        user = TestUser(**user_data)
        await user.save(async_db)

        # Update the user
        new_age = 26
        user.age = new_age
        await user.save(async_db)

        # Find the user to confirm the update
        found_user = await TestUser.find_one(async_db, {"email": user_data["email"]})
        assert found_user is not None
        assert found_user.age == new_age

    @pytest.mark.asyncio
    async def test_delete(self, async_db, test_data):
        """Test deleting a model."""
        # Create and save a user
        user_data = test_data["users"][0]
        user = TestUser(**user_data)
        await user.save(async_db)

        # Delete the user
        result = await user.delete(async_db)
        assert result is True

        # Try to find the deleted user
        found_user = await TestUser.find_one(async_db, {"email": user_data["email"]})
        assert found_user is None

    @pytest.mark.asyncio
    async def test_count(self, async_db, test_data):
        """Test counting documents."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            await user.save(async_db)

        # Count all users
        count = await TestUser.count(async_db)
        assert count == len(test_data["users"])

        # Count with query
        count_over_30 = await TestUser.count(async_db, {"age": {"$gte": 30}})
        assert count_over_30 == 2

    @pytest.mark.asyncio
    async def test_delete_many(self, async_db, test_data):
        """Test deleting multiple documents."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            await user.save(async_db)

        # Delete users over 30
        deleted = await TestUser.delete_many(async_db, {"age": {"$gte": 30}})
        assert deleted == 2

        # Count remaining users
        count = await TestUser.count(async_db)
        assert count == len(test_data["users"]) - 2

    @pytest.mark.asyncio
    async def test_update_many(self, async_db, test_data):
        """Test updating multiple documents."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            await user.save(async_db)

        # Update users under 30
        updated = await TestUser.update_many(
            async_db, {"age": {"$lt": 30}}, {"$set": {"name": "Updated Name"}}
        )
        assert updated == 1

        # Find updated users
        updated_users = await TestUser.find(async_db, {"name": "Updated Name"})
        assert len(updated_users) == 1
        assert updated_users[0].age < 30

    @pytest.mark.asyncio
    async def test_ensure_indexes(self, async_db):
        """Test creating indexes."""
        # Ensure indexes
        await TestUser.ensure_indexes(async_db)

        # This is a basic test just to make sure it doesn't raise an exception
        # In a real environment, we would check the actual indexes
        # but mongomock doesn't fully support index introspection
        assert True

    @pytest.mark.asyncio
    async def test_aggregate(self, async_db, test_data):
        """Test aggregation pipeline."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            await user.save(async_db)

        # Run an aggregation pipeline to get average age
        pipeline = [{"$group": {"_id": None, "avgAge": {"$avg": "$age"}}}]
        result = await TestUser.aggregate(async_db, pipeline)

        # Check result
        assert len(result) == 1
        assert "avgAge" in result[0]
        assert result[0]["avgAge"] == sum(u["age"] for u in test_data["users"]) / len(
            test_data["users"]
        )

    @pytest.mark.asyncio
    async def test_hooks(self, async_db, test_data):
        """Test pre and post save hooks."""
        hook_tracker = {"pre_save_called": False, "post_save_called": False}

        # Define a test class with hooks
        class TestUserWithHooks(TestUser):
            _pre_save_called = False
            _post_save_called = False

            async def pre_save_hook(self):
                hook_tracker["pre_save_called"] = True

            async def post_save_hook(self):
                hook_tracker["post_save_called"] = True

            _pre_save_hooks = [pre_save_hook]
            _post_save_hooks = [post_save_hook]

        # Create and save a user
        user_data = test_data["users"][0]
        user = TestUserWithHooks(**user_data)
        await user.save(async_db)

        print(f"hook_tracker => {hook_tracker}")
        # Check that hooks were called
        assert hook_tracker["pre_save_called"] is True
        assert hook_tracker["post_save_called"] is True
