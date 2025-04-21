from typing import Any, Callable, Dict, List, Optional, TypeVar
from bson import ObjectId
from pydantic import BaseModel
from pymongo import ASCENDING


T = TypeVar("T", bound="MongoModel")


class MongoModel(BaseModel):
    id: Optional[str] = None

    _pre_save_hooks: List[Callable] = []
    _post_save_hooks: List[Callable] = []

    __collection__: str

    __indexes__: Any

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        _instance = super().__new__(cls)

        # object.__setattr__(_instance, "__fields_set__", set())
        return _instance

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @classmethod
    def get_collection(cls, db):

        collection_name = getattr(cls, "__collection__", cls.__name__.lower() + "s")

        print("========================")

        print(collection_name)
        return db[collection_name]

    async def save(self, db) -> T:
        collection = self.get_collection(db)

        if self.id is None:
            result = await collection.insert_one(self.model_dump(exclude={"id"}))
            print(result)

            self.id = str(result.inserted_id)
            print(f"CREATED USER => {self.id}")

        else:
            print(f"update is still called => {self.id}")
            await collection.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": self.model_dump(exclude={"id"})},
            )

        return self

    @classmethod
    async def find_one(cls, db, query: Dict[str, Any]) -> Optional[T]:
        collection = cls.get_collection(db)
        doc = await collection.find_one(query)
        return cls(**doc) if doc else None

    @classmethod
    async def find(cls, db, query: Dict[str, Any] | None = {}) -> List[T]:
        collection = cls.get_collection(db)
        cursor = collection.find(query)

        return cursor

    async def delete(self, db) -> bool:

        if self.id is None:
            return False

        collection = self.get_collection(db)
        result = await collection.delete_one({"_id": ObjectId(self.id)})

        return result.delete_count > 0

    @classmethod
    def ensure_indexes(cls, db):
        collection = cls.get_collection(db)
        index_configs = getattr(cls, "__indexes__", [])

        for index_config in index_configs:
            fields = index_config.get("fields", {})
            kwargs = {k: v for k, v in index_config.items() if k != "fields"}
            print(f"kwargs => {kwargs}")

            processed_fields = []

            for field_spec in fields:
                if isinstance(field_spec, tuple):
                    processed_fields.append(field_spec)
                else:
                    processed_fields.append((field_spec, ASCENDING))

        print(processed_fields)
        collection.create_index(processed_fields, **kwargs)
