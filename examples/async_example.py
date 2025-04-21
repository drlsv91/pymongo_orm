"""
Asynchronous MongoDB ORM example.
"""

import asyncio
import logging
from datetime import datetime

from pymongo_orm import AsyncMongoConnection
from pymongo_orm import setup_logging
from .models.user import AsyncUser


async def run_example():
    """Run the asynchronous example."""
    logger = logging.getLogger("async_example")
    print("Starting async MongoDB example")

    # Create a connection
    connection = AsyncMongoConnection(
        "mongodb://localhost:27017", maxPoolSize=10, appname="AsyncExample"
    )

    # Get the database
    db = connection.get_db(db_name="mongodb_orm_async_examples")

    try:
        # Ensure indexes are created
        await AsyncUser.ensure_indexes(db)

        # Create a user
        user = AsyncUser(
            name="John Doe",
            email="john.doe@example.com",
            age=30,
            bio="Software developer",
            roles=["user", "admin"],
        )

        # Save the user
        await user.save(db)
        print(f"Created user: {user.id}")

        # Update the user
        user.age = 31
        await user.save(db)
        print(f"Updated user age to: {user.age}")

        # Find the user by email
        found_user = await AsyncUser.find_by_email(db, "john.doe@example.com")
        if found_user:
            print(
                f"Found user: {found_user.name}, {found_user.email}, {found_user.age}"
            )

        # Find users with filtering, projection, and sorting
        users = await AsyncUser.find(
            db,
            {"age": {"$gt": 20}},
            projection={"name": 1, "email": 1, "age": 1},
            sort=[("age", -1)],
        )
        print(f"Found {len(users)} users")

        # Update last login time
        await user.update_last_login(db)
        print(f"Updated last login: {user.last_login}")

        # Add and remove roles
        await user.add_role(db, "moderator")
        print(f"User roles after adding: {user.roles}")

        await user.remove_role(db, "admin")
        print(f"User roles after removing: {user.roles}")

        # Count documents
        count = await AsyncUser.count(db, {"is_active": True})
        print(f"Active users count: {count}")

        # Create more users for bulk operations
        users_data = [
            {
                "name": "Alice Smith",
                "email": "alice@example.com",
                "age": 28,
                "roles": ["user"],
            },
            {
                "name": "Bob Johnson",
                "email": "bob@example.com",
                "age": 35,
                "roles": ["user"],
            },
            {
                "name": "Carol Williams",
                "email": "carol@example.com",
                "age": 42,
                "roles": ["user"],
            },
        ]

        created_users = []
        for data in users_data:
            user = AsyncUser(**data)
            await user.save(db)
            created_users.append(user)
            print(f"Created user: {user.name}")

        # Run an aggregation pipeline
        pipeline = [
            {"$group": {"_id": None, "avgAge": {"$avg": "$age"}}},
        ]

        result = await AsyncUser.aggregate(db, pipeline)
        if result:
            print(f"Average age: {result[0]['avgAge']}")

        # Perform batch update
        updated = await AsyncUser.update_many(
            db, {"roles": "user"}, {"$set": {"is_active": True}}
        )
        print(f"Updated {updated} users")

        # Delete a user
        if created_users:
            deleted = await created_users[0].delete(db)
            print(f"Deleted user {created_users[0].name}: {deleted}")

        # Delete many
        deleted_count = await AsyncUser.delete_many(db, {"name": "Bob Johnson"})
        print(f"Deleted {deleted_count} users")

    except Exception as e:
        logger.error(f"Error in async example: {e}")
    finally:
        # Close the connection when done
        connection.close()
        print("Async example completed")


if __name__ == "__main__":
    # Setup logging
    setup_logging(level="INFO")

    # Run the async example
    asyncio.run(run_example())
