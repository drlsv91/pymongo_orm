# pymongo-orm

A lightweight, flexible Object-Relational Mapping (ORM) for MongoDB in Python, designed for asynchronous operations with Pydantic integration.

## 🌟 Features

- **Dual API**: Both synchronous (PyMongo) and asynchronous (Motor) interfaces
- **Type Safety**: Comprehensive type annotations for better IDE support
- **Pydantic Integration**: Powerful data validation and serialization
- **Performance Optimized**: Connection pooling, proper indexing, and efficient queries
- **Hooks System**: Pre/post-save and pre/post-delete hooks
- **Full MongoDB Support**:
  - CRUD operations
  - Advanced queries
  - Projections
  - Sorting, pagination
  - Aggregation pipelines
  - Bulk operations
  - Indexing
- **Modular Design**: Well-structured code with proper separation of concerns
- **Error Handling**: Comprehensive error handling and custom exceptions
- **Logging**: Built-in logging for debugging and monitoring

## 📦 Installation

Install using pip:

```bash
pip install pymongo-orm
```

Or with Poetry:

```bash
poetry add pymongo-orm
```

## Quick Start

### Async Example

```python
import asyncio
from pymongo_orm import AsyncMongoModel, AsyncMongoConnection
from pydantic import Field

# Define your model
class User(AsyncMongoModel):
    __collection__ = "users"

    name: str = Field(..., min_length=2)
    email: str
    age: int

# Use the model
async def main():
    # Connect to MongoDB
    conn = AsyncMongoConnection("mongodb://localhost:27017")
    db = conn.get_db(db_name="mydb")

    # Create and save a user
    user = User(name="John Doe", email="john@example.com", age=30)
    await user.save(db)

    # Find users
    users = await User.find(db, {"age": {"$gt": 25}})
    for user in users:
        print(f"Found user: {user.name}, {user.email}")

    # Close connection
    conn.close()

# Run the example
asyncio.run(main())
```

### Sync Example

```python
from  pymongo_orm import SyncMongoModel, SyncMongoConnection
from pydantic import Field

# Define your model
class User(SyncMongoModel):
    __collection__ = "users"

    name: str = Field(..., min_length=2)
    email: str
    age: int

# Use the model
def main():
    # Connect to MongoDB
    conn = SyncMongoConnection("mongodb://localhost:27017")
    db = conn.get_db(db_name="mydb")

    # Create and save a user
    user = User(name="Jane Doe", email="jane@example.com", age=28)
    user.save(db)

    # Find users
    users = User.find(db, {"age": {"$gt": 25}})
    for user in users:
        print(f"Found user: {user.name}, {user.email}")

    # Close connection
    conn.close()

# Run the example
if __name__ == "__main__":
    main()
```

## Advanced Usage

The Mongomodel supports advanced MongoDB features:

### Indexes

```python
from pymongo import ASCENDING, DESCENDING

class User(AsyncMongoModel):
    __collection__ = "users"
    __indexes__ = [
        {"fields": [("email", ASCENDING)], "unique": True},
        {"fields": [("name", ASCENDING), ("age", DESCENDING)]}
    ]

    name: str
    email: str
    age: int

# Create indexes
await User.ensure_indexes(db)
```

### Aggregation

```python
pipeline = [
    {"$match": {"age": {"$gt": 30}}},
    {"$group": {"_id": None, "avgAge": {"$avg": "$age"}}}
]
results = await User.aggregate(db, pipeline)
```

### Bulk Operations

```python
from pymongo import InsertOne, UpdateOne, DeleteOne

operations = [
    InsertOne({"name": "User 1", "email": "user1@example.com", "age": 25}),
    UpdateOne({"email": "user2@example.com"}, {"$set": {"age": 26}}),
    DeleteOne({"email": "user3@example.com"})
]

result = await User.bulk_write(db, operations)
```

## Project Structure

```
pymongo_orm/
├── src/
│   └── pymongo_orm/           # Main package
│       ├── abstract/          # Abstract base classes
│       ├── async_/            # Async implementation
│       ├── sync/              # Sync implementation
│       ├── utils/             # Utility functions
│       └── ...
├── examples/                  # Usage examples
├── tests/                     # Test suite
└── ...
```

## 📋 Requirements

- Python 3.9+
- pymongo
- motor
- pydantic

## Development

Setup development environment:

```bash
# Clone the repository
git clone https://github.com/drlsv91/pymongo_orm.git
cd pymongo_orm

# Create and activate a virtual environment
poetry env activate # On Windows: venv\Scripts\activate

# Install the package in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
