"""
Example User models for MongoDB ORM.
"""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import EmailStr, Field, validator
from pymongo import ASCENDING, DESCENDING

from mongomodel.sync_model.model import SyncMongoModel
from mongomodel.async_model.model import AsyncMongoModel


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


class AsyncUser(AsyncMongoModel, UserBase):
    """
    Asynchronous User model.

    This model represents a user in the system and provides asynchronous
    MongoDB operations.
    """

    # Collection configuration
    __collection__ = "users"
    __indexes__ = [
        {"fields": [("email", ASCENDING)], "unique": True, "background": True},
        {
            "fields": [("name", ASCENDING), ("age", DESCENDING)],
            "sparse": True,
            "background": True,
        },
        {"fields": [("is_active", ASCENDING)], "background": True},
        {"fields": [("roles", ASCENDING)], "background": True},
    ]
    __write_concern__ = {"w": "majority", "j": True}

    # Fields
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=0, le=120)
    bio: Optional[str] = Field(None, max_length=500)
    roles: List[str] = Field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None
    metadata: dict = Field(default_factory=dict)

    # Register hooks
    _pre_save_hooks = [UserBase.before_save]
    _post_save_hooks = [UserBase.after_save]

    # Custom async methods
    async def update_last_login(self, db):
        """Update the last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        await self.save(db)

    async def add_role(self, db, role: str):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            await self.save(db)

    async def remove_role(self, db, role: str):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            await self.save(db)

    @classmethod
    async def find_by_email(cls, db, email: str):
        """Find a user by email (case-insensitive)."""
        return await cls.find_one(db, {"email": email.lower()})

    @classmethod
    async def find_active_users(cls, db):
        """Find all active users."""
        return await cls.find(db, {"is_active": True})

    @classmethod
    async def find_users_by_role(cls, db, role: str):
        """Find all users with a specific role."""
        return await cls.find(db, {"roles": role})


class SyncUser(SyncMongoModel, UserBase):
    """
    Synchronous User model.

    This model represents a user in the system and provides synchronous
    MongoDB operations.
    """

    # Collection configuration
    __collection__ = "users"
    __indexes__ = [
        {"fields": [("email", ASCENDING)], "unique": True, "background": True},
        {
            "fields": [("name", ASCENDING), ("age", DESCENDING)],
            "sparse": True,
            "background": True,
        },
        {"fields": [("is_active", ASCENDING)], "background": True},
        {"fields": [("roles", ASCENDING)], "background": True},
    ]
    __write_concern__ = {"w": "majority", "j": True}

    # Fields
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=0, le=120)
    bio: Optional[str] = Field(None, max_length=500)
    roles: List[str] = Field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None
    metadata: dict = Field(default_factory=dict)

    # Register hooks
    _pre_save_hooks = [UserBase.before_save]
    _post_save_hooks = [UserBase.after_save]

    # Custom sync methods
    def update_last_login(self, db):
        """Update the last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        self.save(db)

    def add_role(self, db, role: str):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            self.save(db)

    def remove_role(self, db, role: str):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            self.save(db)

    @classmethod
    def find_by_email(cls, db, email: str):
        """Find a user by email (case-insensitive)."""
        return cls.find_one(db, {"email": email.lower()})

    @classmethod
    def find_active_users(cls, db):
        """Find all active users."""
        return cls.find(db, {"is_active": True})

    @classmethod
    def find_users_by_role(cls, db, role: str):
        """Find all users with a specific role."""
        return cls.find(db, {"roles": role})
