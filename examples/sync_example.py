"""
Synchronous MongoDB ORM example.
"""

import logging
from datetime import datetime, timezone

import pymongo

from examples.models.user import SyncUser
from pymongo_orm import SyncMongoConnection, setup_logging


def run_example():
    """Run the synchronous example."""
    logger = logging.getLogger("sync_example")
    print("Starting sync MongoDB example")

    # Create a connection
    connection = SyncMongoConnection(
        "mongodb://localhost:27017",
        maxPoolSize=10,
        appname="SyncExample",
    )

    # Get the database
    db = connection.get_db(db_name="sync_examples")

    try:
        # Ensure indexes are created
        SyncUser.ensure_indexes(db)

        # Create a user
        user = SyncUser(
            name="Jane Doe",
            email="jane.doe@example.com",
            age=28,
            bio="Data scientist",
            roles=["user", "analyst"],
        )

        # Save the user
        user.save(db)
        print(f"Created user: {user.id}")

        # Update the user
        user.age = 29
        user.save(db)
        print(f"Updated user age to: {user.age}")

        # Find the user by email
        found_user = SyncUser.find_by_email(db, "jane.doe@example.com")
        if found_user:
            print(
                f"Found user: {found_user.name}, {found_user.email}, {found_user.age}",
            )

        # Find users with filtering, projection, and sorting
        users = SyncUser.find(
            db,
            {"age": {"$gt": 20}},
            projection={"name": 1, "email": 1, "age": 1},
            sort=[("age", pymongo.DESCENDING)],
        )
        print(f"Found {len(users)} users")

        # Update last login time
        user.update_last_login(db)
        print(f"Updated last login: {user.last_login}")

        # Add and remove roles
        user.add_role(db, "researcher")
        print(f"User roles after adding: {user.roles}")

        user.remove_role(db, "analyst")
        print(f"User roles after removing: {user.roles}")

        # Count documents
        count = SyncUser.count(db, {"is_active": True})
        print(f"Active users count: {count}")

        # Create more users for bulk operations
        users_data = [
            {
                "name": "David Brown",
                "email": "david@example.com",
                "age": 32,
                "roles": ["user"],
            },
            {
                "name": "Emma Davis",
                "email": "emma@example.com",
                "age": 27,
                "roles": ["user"],
            },
            {
                "name": "Frank Miller",
                "email": "frank@example.com",
                "age": 45,
                "roles": ["user"],
            },
        ]

        created_users = []
        for data in users_data:
            user = SyncUser(**data)
            user.save(db)
            created_users.append(user)
            print(f"Created user: {user.name}")

        # Run an aggregation pipeline
        pipeline = [
            {"$group": {"_id": None, "avgAge": {"$avg": "$age"}}},
        ]

        result = SyncUser.aggregate(db, pipeline)
        if result:
            print(f"Average age: {result[0]['avgAge']}")

        # Perform batch update
        updated = SyncUser.update_many(
            db,
            {"roles": "user"},
            {"$set": {"is_active": True}},
        )
        print(f"Updated {updated} users")

        # Delete a user
        if created_users:
            deleted = created_users[0].delete(db)
            print(f"Deleted user {created_users[0].name}: {deleted}")

        # Delete many
        deleted_count = SyncUser.delete_many(db, {"name": "Emma Davis"})
        print(f"Deleted {deleted_count} users")

        # Demonstrate bulk write operations
        from pymongo import DeleteOne, InsertOne, UpdateOne

        bulk_operations = [
            InsertOne(
                {
                    "name": "Grace Wilson",
                    "email": "grace@example.com",
                    "age": 38,
                    "roles": ["user"],
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                },
            ),
            UpdateOne({"email": "frank@example.com"}, {"$set": {"age": 46}}),
            DeleteOne({"email": "nonexistent@example.com"}),
        ]

        bulk_result = SyncUser.bulk_write(db, bulk_operations)
        print(
            f"Bulk write results: {bulk_result.inserted_count} inserted, "
            f"{bulk_result.modified_count} modified, {bulk_result.deleted_count} deleted",
        )

    except Exception as e:
        logger.error(f"Error in sync example: {e}")
    finally:
        # Close the connection when done
        connection.close()
        print("Sync example completed")


if __name__ == "__main__":
    # Setup logging
    setup_logging(level="INFO")

    # Run the async example
    run_example()
