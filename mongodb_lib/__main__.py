import asyncio
import threading
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from .model import MongoModel


class AsyncMongoConnection:
    _instances = {}
    _look = threading.Lock()

    def __new__(cls, uri: str):
        with cls._look:
            if uri not in cls._instances:
                instance = super().__new__(cls)
                instance._client = AsyncIOMotorClient(uri)
                cls._instances[uri] = instance
            return cls._instances[uri]

    def get_db(self, *, db_name: str):
        return self._client[db_name]


connect = AsyncMongoConnection("mongodb://localhost:27017/learning_db")


class User(MongoModel):
    __collection__ = "users_details"
    __indexes__ = [
        {"fields": [("email", ASCENDING)], "unique": True},  # Single field
        {
            "fields": [("name", ASCENDING), ("age", DESCENDING)],
            "sparse": True,
        },  # Compound
    ]
    name: str
    email: str
    age: int


async def main():
    db = connect.get_db(db_name="testing_users")

    User.ensure_indexes(db)
    user = User(name="john doe", email="user@mail.com", age=32)
    await user.save(db)
    user.email = "user2@yopmail.com"
    await user.save(db)

    user_one = await user.find_one(db, {"email": "user2@yopmail.com"})

    print(user)
    print(user_one)
    user2 = User(email="user2@yopmail.com", name="user 2", age=40)
    await user2.save(db)

    users = await User.find(db)
    print(users)


asyncio.run(main())
