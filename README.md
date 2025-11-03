<!-- TOC --><a name="create-fastapi-app"></a>
# Create-FastAPI-App

A CLI tool to quickly scaffold production-ready FastAPI applications with a well-structured project template.
<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

## Table of Contents

- [Create-FastAPI-App](#create-fastapi-app)
   * [Features](#features)
   * [Requirements](#requirements)
   * [Quick Start](#quick-start)
   * [Project Structure](#project-structure)
      + [Root Directory](#root-directory)
      + [alembic/](#alembic)
      + [app/](#app)
         - [app/main.py](#appmainpy)
         - [app/database/](#appdatabase)
         - [app/dtos/](#appdtos)
         - [app/routers/](#approuters)
         - [app/utils/](#apputils)
      + [scripts/](#scripts)
      + [test/](#test)
   * [Development Workflow](#development-workflow)
      + [Adding a new feature](#adding-a-new-feature)
      + [Database migrations](#database-migrations)
      + [Running tests](#running-tests)
      + [Code quality](#code-quality)
   * [Docker](#docker)
   * [Environment Variables](#environment-variables)
   * [TODO](#todo)
   * [License](#license)
   * [Contributing](#contributing)

<!-- TOC end -->

<!-- TOC --><a name="features"></a>
## Features

- Interactive CLI for project creation
- Pre-configured FastAPI application with best practices (I think 💀)
- PostgreSQL database integration with SQLAlchemy and Alembic migrations
- Type-safe settings management with Pydantic
- Docker support for containerized deployment
- Pre-commit hooks for code quality
- Testing setup with pytest
- Type checking with Pyright
- Code formatting and linting with Ruff

<!-- TOC --><a name="requirements"></a>
## Requirements

- uv (Python package manager)
- Git
- PostgreSQL (for database integration)
- Docker (optional, for containerization)

<!-- TOC --><a name="quick-start"></a>
## Quick Start

Run the CLI tool to create a new FastAPI project:

```bash
uvx git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

The CLI will prompt you for:

- **Project name**: The name of your application
- **Project description**: A brief description of your application
- **Initialize git repository**: Whether to create a git repository with an initial commit
- **Setup database**: Whether to set up create the database and run initial migrations

<!-- TOC --><a name="project-structure"></a>
## Project Structure

The generated template follows a clean architecture pattern with clear separation of concerns:

<!-- TOC --><a name="root-directory"></a>
### Root Directory

```
your-project-name/
├── alembic.ini              # Alembic configuration for database migrations
├── conftest.py              # Pytest configuration and shared fixtures
├── Dockerfile               # Docker container configuration
├── pyproject.toml           # Project metadata and dependencies
├── pyrightconfig.json       # Pyright type checker configuration
├── pytest.ini               # Pytest configuration
└── README.md                # Project documentation
```

<!-- TOC --><a name="alembic"></a>
### alembic/

Database migration management using Alembic.

```
alembic/
├── env.py                   # Alembic environment configuration
├── script.py.mako           # Template for generating migration scripts
└── versions/                # Directory for migration version files
```

**Usage:**

- Create a new migration: `uv run python -m scripts.create_migration "description"`
- Apply migrations: `uv run alembic upgrade head`
- Rollback migrations: `uv run alembic downgrade -1`

<!-- TOC --><a name="app"></a>
### app/

Main application code.

```
app/
├── __init__.py
├── main.py                  # FastAPI application entry point and configuration
├── database/                # Database configuration and models
├── dtos/                    # Data Transfer Objects (Pydantic models)
├── routers/                 # API route handlers
└── utils/                   # Utility modules
```

<!-- TOC --><a name="appmainpy"></a>
#### app/main.py

The core application file that:

- Creates and configures the FastAPI application
- Sets up CORS middleware
- Registers API routers
- Manages application lifespan (startup/shutdown)
- Configures API documentation

**Key functions:**

- `create_app()`: Main application factory
- `include_routers()`: Register your API routers here
- `add_middlewares()`: Add custom middlewares here

<!-- TOC --><a name="appdatabase"></a>
#### app/database/

Database-related code.

```
database/
├── __init__.py
├── session.py               # Database session management and engine configuration
└── models/                  # SQLAlchemy models
    ├── __init__.py
    └── base.py              # Base model class for all database models
```

**Usage:**

- Define new models in `models/` directory
- Import them in `models/__init__.py`
- Use async sessions from `session.py` for database operations

<!-- TOC --><a name="appdtos"></a>
#### app/dtos/

Data Transfer Objects using Pydantic.

```
dtos/
└── __init__.py
```

**Usage:**

- Create request/response schemas here
- Use for API request validation and response serialization
- Example: `UserCreate`, `UserResponse`, `TokenResponse`

<!-- TOC --><a name="approuters"></a>
#### app/routers/

API route handlers.

```
routers/
├── __init__.py
├── health.py                # Health check endpoint
└── root.py                  # Root endpoint
```

**Usage:**

- Create new routers for different API resources
- Each router should focus on a specific domain (e.g., `users.py`, `auth.py`)
- Register new routers in `app/main.py` in the `include_routers()` function

Example router structure:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/")
async def list_users():
    return {"users": []}
```

<!-- TOC --><a name="apputils"></a>
#### app/utils/

Utility modules and shared functionality.

```
utils/
├── error.py                 # Custom exception classes
├── logger.py                # Logging configuration
└── settings.py              # Application settings using Pydantic
```

**settings.py**:

- Manages environment variables
- Type-safe configuration
- Automatic validation with Pydantic
- Add new settings as class attributes

**logger.py**:

- Pre-configured logging
- Import and use throughout the application

**error.py**:

- Define custom exceptions here
- Use for domain-specific errors

<!-- TOC --><a name="scripts"></a>
### scripts/

Utility scripts for development and deployment.

```
scripts/
├── __init__.py
├── create_migration.py      # Helper script to create Alembic migrations
├── setup_db.py              # Database setup and initialization script
└── utils.py                 # Shared utility functions for scripts
```

**Usage:**

- `setup_db.py`: Run to set up the database (checks PostgreSQL, creates DB, runs migrations)
- `create_migration.py`: Run to create a new migration after changing models
- Add custom management scripts here (e.g., seed data, cleanup tasks)

<!-- TOC --><a name="test"></a>
### test/

Test suite using pytest.

```
test/
├── __init__.py
└── test_api.py              # API endpoint tests
```

**Usage:**

- Write unit tests for business logic
- Write integration tests for API endpoints
- Use `conftest.py` for shared fixtures
- Run tests: `pytest`
- Run with coverage: `pytest --cov=app`

<!-- TOC --><a name="development-workflow"></a>
## Development Workflow

<!-- TOC --><a name="adding-a-new-feature"></a>
### Adding a new feature

1. **Create database models** in `app/database/models/`
2. **Create a migration**: `uv run python -m scripts.create_migration "add user table"`
3. **Apply the migration**: `uv run alembic upgrade head`
4. **Create DTOs** in `app/dtos/` for request/response validation
5. **Create router** in `app/routers/` with your endpoints
6. **Register router** in `app/main.py`
7. **Write tests** in `test/`

<!-- TOC --><a name="database-migrations"></a>
### Database migrations

```bash
# Create a migration after changing models
uv run python -m scripts.create_migration "description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

<!-- TOC --><a name="running-tests"></a>
### Running tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest test/test_api.py

# Run with verbose output
uv run pytest -v
```

<!-- TOC --><a name="code-quality"></a>
### Code quality

The project includes pre-commit hooks for:

- Ruff (linting and formatting)
- Pyright (type checking)

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

<!-- TOC --><a name="docker"></a>
## Docker

Build and run with Docker:

```bash
# Build image
docker build -t your-app-name .

# Run container
docker run -p 8000:8000 your-app-name
```

<!-- TOC --><a name="environment-variables"></a>
## Environment Variables

Key environment variables (configure in `.env`):

| Variable            | Description                                  | Default                                                                  |
| ------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| `APP_NAME`          | Application name                             | Generated from CLI                                                       |
| `APP_DESCRIPTION`   | Application description                      | Generated from CLI                                                       |
| `APP_VERSION`       | Application version                          | 0.1.0                                                                    |
| `ENV`               | Environment (development/production/testing) | development                                                              |
| `FASTAPI_DEBUG`     | Debug mode                                   | false                                                                    |
| `FASTAPI_HOST`      | Server host                                  | 0.0.0.0                                                                  |
| `FASTAPI_PORT`      | Server port                                  | 8000                                                                     |
| `FASTAPI_RELOAD`    | Auto-reload on code changes                  | true                                                                     |
| `FASTAPI_LOG_LEVEL` | Logging level                                | info                                                                     |
| `CORS_ORIGINS`      | Allowed CORS origins                         | []                                                                       |
| `DATABASE_URL`      | PostgreSQL connection string                 | postgresql+asyncpg://postgres:postgres@localhost:5432/{{APP_NAME}}       |
| `TEST_DATABASE_URL` | Test database connection string              | postgresql+asyncpg://postgres:postgres@localhost:5432/{{APP_NAME}}\_test |

<!-- TOC --><a name="todo"></a>
## TODO

- Fix reload includes and excludes not working.

<!-- TOC --><a name="license"></a>
## License

MIT

<!-- TOC --><a name="contributing"></a>
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
