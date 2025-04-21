# Contributing to PyMongo ORM

Thank you for your interest in contributing to PyMongo ORM! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment](#development-environment)
  - [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
  - [Creating a Branch](#creating-a-branch)
  - [Making Changes](#making-changes)
  - [Testing](#testing)
  - [Code Style](#code-style)
  - [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct. Please report unacceptable behavior to [maintainer email].

## Getting Started

### Development Environment

1. **Fork the repository** on GitHub.

2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/pymongo-orm.git
   cd pymongo-orm
   ```

3. **Set up the upstream remote**:

   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/pymongo-orm.git
   ```

4. **Create a virtual environment** and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install the package in development mode with dev dependencies
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install
   ```

5. **MongoDB Setup**:
   - For development, you can use a local MongoDB instance or Docker:
     ```bash
     docker run -d -p 27017:27017 --name mongodb mongo:latest
     ```

### Project Structure

```
pymongo_orm/
├── src/
│   └── pymongo_orm/         # Main package
│       ├── abstract/        # Abstract base classes
│       ├── async_/          # Async implementation
│       ├── sync/            # Sync implementation
│       ├── utils/           # Utility functions
│       └── ...
├── examples/                # Usage examples
├── tests/                   # Test suite
└── ...
```

## Development Workflow

### Creating a Branch

1. **Update your fork** with the latest changes from upstream:

   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

### Making Changes

1. **Implement your changes** following the project's code style.

2. **Write tests** for your changes to ensure they work as expected.

3. **Update documentation** as needed.

4. **Run pre-commit checks** before committing:

   ```bash
   pre-commit run --all-files
   ```

5. **Commit your changes** with a clear and descriptive commit message:
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

### Testing

1. **Run tests** to ensure your changes don't break existing functionality:

   ```bash
   pytest
   ```

2. **Run with coverage** to ensure adequate test coverage:

   ```bash
   pytest --cov=pymongo_orm tests/
   ```

3. **Write new tests** for your features or bug fixes.

### Code Style

This project uses:

- **black** for code formatting
- **isort** for import sorting
- **mypy** for type checking
- **ruff** for linting

You can run all style checks with:

```bash
black src tests
isort src tests
mypy src
ruff src tests
```

### Documentation

- **Update docstrings** for all public modules, functions, classes, and methods
- **Follow the Google docstring style**
- **Update README.md** if your changes affect usage

## Pull Request Process

1. **Push your changes** to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request** to the `main` branch of the original repository.

3. **Fill in the pull request template** with:

   - Description of changes
   - Issue number(s) addressed
   - Any breaking changes
   - Screenshots or examples (if applicable)

4. **Address review comments** and make requested changes.

5. **Ensure CI passes** on your pull request.

6. A maintainer will merge your pull request once it's ready.

## Release Process

Releases are managed by maintainers using the following process:

1. **Update version number** in `src/pymongo_orm/__init__.py` and `pyproject.toml`
2. **Update CHANGELOG.md** with changes for the new version
3. **Create a tag** for the new version
4. **Build and publish** to PyPI

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

Thank you for contributing to PyMongo ORM!
