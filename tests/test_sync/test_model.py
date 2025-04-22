"""
Tests for the synchronous MongoDB model implementation.
"""

from pymongo import ASCENDING

from pymongo_orm.sync_model.model import SyncMongoModel


class TestUser(SyncMongoModel):
    """Test user model for synchronous operations."""

    __collection__ = "users"
    __indexes__ = [{"fields": [("email", ASCENDING)], "unique": True}]

    name: str
    email: str
    age: int


class TestSyncModel:
    """Tests for synchronous MongoDB models."""

    def test_create_and_save(self, sync_db, test_data):
        """Test creating and saving a model."""
        # Create a new user
        user_data = test_data["users"][0]
        user = TestUser(**user_data)

        # Save the user
        saved_user = user.save(sync_db)

        # Check that the user was saved
        assert saved_user.id is not None
        assert saved_user.name == user_data["name"]
        assert saved_user.email == user_data["email"]
        assert saved_user.age == user_data["age"]

        # Find the user to confirm it was saved
        found_user = TestUser.find_one(sync_db, {"email": user_data["email"]})
        assert found_user is not None
        assert found_user.id == saved_user.id
        assert found_user.name == user_data["name"]

    def test_find_and_query(self, sync_db, test_data):
        """Test finding and querying models."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            user.save(sync_db)

        # Test find all
        all_users = TestUser.find(sync_db)
        assert len(all_users) == len(test_data["users"])

        # # Test find with query
        users_over_30 = TestUser.find(sync_db, {"age": {"$gte": 30}})
        assert len(users_over_30) == 2
        assert all(user.age >= 30 for user in users_over_30)

        # # Test find with projection
        users_with_projection = TestUser.find(
            sync_db,
            projection={"name": 1, "email": 1, "age": 1},
        )
        assert len(users_with_projection) == len(test_data["users"])
        assert hasattr(users_with_projection[0], "name")
        assert hasattr(users_with_projection[0], "email")

        # # Test find with sorting
        users_sorted = TestUser.find(sync_db, sort=[("age", -1)])
        assert users_sorted[0].age > users_sorted[-1].age

    def test_update(self, sync_db, test_data):
        """Test updating a model."""
        # Create and save a user
        user_data = test_data["users"][0]
        user = TestUser(**user_data)
        user.save(sync_db)

        # Update the user
        new_age = 26
        user.age = new_age
        user.save(sync_db)

        # Find the user to confirm the update
        found_user = TestUser.find_one(sync_db, {"email": user_data["email"]})
        assert found_user is not None
        assert found_user.age == new_age

    def test_delete(self, sync_db, test_data):
        """Test deleting a model."""
        # Create and save a user
        user_data = test_data["users"][0]
        user = TestUser(**user_data)
        user.save(sync_db)

        # Delete the user
        result = user.delete(sync_db)
        assert result is True

        # Try to find the deleted user
        found_user = TestUser.find_one(sync_db, {"email": user_data["email"]})
        assert found_user is None

    def test_count(self, sync_db, test_data):
        """Test counting documents."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            user.save(sync_db)

        # Count all users
        count = TestUser.count(sync_db)
        assert count == len(test_data["users"])

        # Count with query
        count_over_30 = TestUser.count(sync_db, {"age": {"$gte": 30}})
        assert count_over_30 == 2

    def test_delete_many(self, sync_db, test_data):
        """Test deleting multiple documents."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            user.save(sync_db)

        # Delete users over 30
        deleted = TestUser.delete_many(sync_db, {"age": {"$gte": 30}})
        assert deleted == 2

        # Count remaining users
        count = TestUser.count(sync_db)
        assert count == len(test_data["users"]) - 2

    def test_update_many(self, sync_db, test_data):
        """Test updating multiple documents."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            user.save(sync_db)

        # Update users under 30
        updated = TestUser.update_many(
            sync_db,
            {"age": {"$lt": 30}},
            {"$set": {"name": "Updated Name"}},
        )
        assert updated == 1

        # Find updated users
        updated_users = TestUser.find(sync_db, {"name": "Updated Name"})
        assert len(updated_users) == 1
        assert updated_users[0].age < 30

    def test_ensure_indexes(self, sync_db):
        """Test creating indexes."""
        # Ensure indexes
        TestUser.ensure_indexes(sync_db)

        # This is a basic test just to make sure it doesn't raise an exception
        # In a real environment, we would check the actual indexes
        # but mongomock doesn't fully support index introspection
        assert True

    def test_aggregate(self, sync_db, test_data):
        """Test aggregation pipeline."""
        # Create and save multiple users
        for user_data in test_data["users"]:
            user = TestUser(**user_data)
            user.save(sync_db)

        # Run an aggregation pipeline to get average age
        pipeline = [{"$group": {"_id": None, "avgAge": {"$avg": "$age"}}}]
        result = TestUser.aggregate(sync_db, pipeline)

        # Check result
        assert len(result) == 1
        assert "avgAge" in result[0]
        assert result[0]["avgAge"] == sum(u["age"] for u in test_data["users"]) / len(
            test_data["users"],
        )

    def test_hooks(self, sync_db, test_data):
        """Test pre and post save hooks."""

        # Define a test class with hooks
        class TestUserWithHooks(TestUser):
            _pre_save_called = False
            _post_save_called = False

            def pre_save_hook(self):
                TestUserWithHooks._pre_save_called = True

            def post_save_hook(self):
                TestUserWithHooks._post_save_called = True

            _pre_save_hooks = [pre_save_hook]
            _post_save_hooks = [post_save_hook]

        # Create and save a user
        user_data = test_data["users"][0]
        user = TestUserWithHooks(**user_data)
        user.save(sync_db)

        # Check that hooks were called
        assert TestUserWithHooks._pre_save_called is True
        assert TestUserWithHooks._post_save_called is True
