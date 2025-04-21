import asyncio
from datetime import datetime
from typing import List, Optional

from pydantic import Field, validator
from pymongo import ASCENDING, DESCENDING

from ..async_model.connection import AsyncMongoConnection
from ..async_model.model import AsyncMongoModel


connect = AsyncMongoConnection("mongodb://localhost:27017/learning_db")


class UserBase:
    """Common base fields and methods for User models."""

    # Validators
    @validator("email")
    def email_must_be_valid(cls, v):
        """Validate email format."""
        if not v or "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @validator("age")
    def age_must_be_valid(cls, v):
        """Validate age is within reasonable range."""
        if v < 0 or v > 120:
            raise ValueError("Age must be between 0 and 120")
        return v

    # Hooks
    def before_save(self):
        """Hook that runs before saving."""
        self.name = self.name.strip()
        self.email = self.email.lower()

    def after_save(self):
        """Hook that runs after saving."""
        print(f"User {self.name} ({self.email}) saved successfully")

    # Business logic methods
    def is_adult(self) -> bool:
        """Check if user is an adult (18+ years old)."""
        return self.age >= 18

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles


class User(AsyncMongoModel, UserBase):
    __collection__ = "users_async"
    __indexes__ = [
        {
            "fields": [("email", ASCENDING)],
            "unique": True,
            "background": True,
        },  # Single field
        {
            "fields": [("name", ASCENDING), ("age", DESCENDING)],
            "sparse": True,
            "background": True,
        },  # Compound
    ]

    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=0, le=120)
    bio: Optional[str] = Field(None, max_length=500)
    roles: List[str] = Field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None
    metadata: Optional[dict] = Field(default_factory=dict)

    # Register hooks
    _pre_save_hooks = [UserBase.before_save]
    _post_save_hooks = [UserBase.after_save]


async def async_func():
    db = connect.get_db(db_name="testing_users")

    await User.ensure_indexes(db)
    user = User(name="john doe", email="user@mail.com", age=32, roles=["admin"])
    await user.save(db)
    user.email = "user1@yopmail.com"
    await user.save(db)

    user_one = await user.find_one(db, {"email": "user2@yopmail.com"})

    print(user)
    print(user_one)
    user2 = User(email="user2@yopmail.com", name="user 2", age=40, roles=["admin"])
    await user2.save(db)

    users = await User.find(db)
    print(users)
