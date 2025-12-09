<!-- TOC --><a name="{{APP-NAME}}"></a>

# {{APP-NAME}}

{{APP-DESCRIPTION}}

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

## Table of Contents

- [{{APP-NAME}}](#app-name)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Quick Start](#quick-start)
  - [Project Structure](#project-structure)
    - [Root Directory](#root-directory)
    - [alembic/](#alembic)
    - [app/](#app)
      - [app/main.py](#appmainpy)
      - [app/database/](#appdatabase)
      - [app/models/](#appmodels)
      - [app/dtos/](#appdtos)
      - [app/routers/](#approuters)
      - [app/services/](#appservices)
      - [app/utils/](#apputils)
    - [scripts/](#scripts)
    - [test/](#test)
  - [Development Workflow](#development-workflow)
    - [Adding a new feature](#adding-a-new-feature)
    - [Database migrations](#database-migrations)
    - [Running tests](#running-tests)
    - [Code quality](#code-quality)
  - [Docker](#docker)
  - [Environment Variables](#environment-variables)

<!-- TOC end -->

<!-- TOC --><a name="features"></a>

## Features

- Pre-configured FastAPI application with best practices
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

1. Install dependencies:

```bash
uv sync
```

2. Set up environment variables (copy `.env.example` to `.env` and configure):

```bash
cp .env.example .env
```

3. Set up the database:

```bash
bash scripts/setup_db.sh
```

4. Run the application:

```bash
bash scripts/start_server.sh
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

<!-- TOC --><a name="project-structure"></a>

## Project Structure

The project follows a clean architecture pattern with clear separation of concerns:

<!-- TOC --><a name="root-directory"></a>

### Root Directory

```
{{APP-NAME}}/
├── alembic.ini              # Alembic configuration for database migrations
├── conftest.py              # Pytest configuration and shared fixtures
├── docker-compose.yml       # Docker Compose configuration
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

- Create a new migration: `uv run alembic revision --autogenerate -m "description"`
- Apply migrations: `uv run alembic upgrade head`
- Rollback migrations: `uv run alembic downgrade -1`

<!-- TOC --><a name="app"></a>

### app/

Main application code.

```
app/
├── __init__.py
├── __main__.py              # Application entry point
├── main.py                  # FastAPI application factory and configuration
├── database/                # Database configuration
├── dtos/                    # Data Transfer Objects (Pydantic models)
├── models/                  # SQLAlchemy models
├── routers/                 # API route handlers
├── services/                # Business logic layer
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
- `add_middlewares()`: Add custom middlewares here

<!-- TOC --><a name="appdatabase"></a>

#### app/database/

Database-related code.

```
database/
├── __init__.py
└── session.py               # Database session management and engine configuration
```

**Usage:**

- Use async sessions from `session.py` for database operations
- Import `get_db_session` dependency for route handlers

<!-- TOC --><a name="appmodels"></a>

#### app/models/

SQLAlchemy database models.

```
models/
├── __init__.py
└── base.py                  # Base model class for all database models
```

**Usage:**

- Define new models in this directory
- All models should inherit from the `Base` class

Example model:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
```

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
├── root.py                  # Root endpoint
└── routes.py                # Centralized router registration
```

**Usage:**

- Create new routers for different API resources (e.g., `users.py`, `auth.py`)
- Register new routers in `routes.py` for centralized management

Example router registration (`routes.py`):

```python
# app/routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/")
async def list_users():
    return {"users": []}
```

```python
# app/routers/routes.py
from app.routers.users import router as users_router
...
root_router.include_router(users_router)
```

<!-- TOC --><a name="appservices"></a>

#### app/services/

Business logic layer.

```
services/
└── __init__.py
```

**Usage:**

- Create service classes for business logic
- Keep routers thin by moving complex logic to services
- Services should handle database operations, external API calls, etc.

Example service:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User | None:
        # Business logic here
        pass
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
├── start_server.sh          # Production server script
├── setup_db.sh              # Database initialization script
├── reset_db.sh              # Drop and recreate database script
├── migrate.sh               # Database migration script
├── test.sh                  # Test runner script
├── utils.sh                 # Shared shell script utilities
├── db/                      # Database management modules
│   ├── __init__.py
│   ├── setup.py             # Database creation logic
│   ├── drop.py              # Database drop logic
│   └── utils/               # Database utilities
└── utils/                   # Script utility modules
    └── utils.py             # Python utility functions
```

**Usage:**

- `start_server.sh`: Start server (supports --testing flag for test environment)
- `setup_db.sh`: Initialize database (checks PostgreSQL, creates DB, runs migrations)
- `reset_db.sh`: Drop and recreate database with fresh migrations (supports --testing flag)
- `migrate.sh`: Apply pending database migrations (supports --testing flag)
- `test.sh`: Run pytest test suite
- `utils.sh`: Provides shared functions like `parse_args()` and `run_with_env()` for other scripts

**Note:** Scripts support `--testing` flag to run against test database. The flag is automatically handled by `utils.sh` which sets `ENV=testing` for the command.

**Important:** The scripts use shell script wrappers (`.sh` files) that call Python modules. This approach does not maintain backwards compatibility with older versions that used Python scripts directly. Always use the shell scripts (e.g., `bash scripts/setup_db.sh`) rather than calling Python modules directly.

<!-- TOC --><a name="test"></a>

### test/

Test suite using pytest.

```
test/
├── __init__.py
└── test_health.py           # Health check endpoint tests
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

1. **Create database models** in `app/models/`
2. **Create a migration**: `uv run alembic revision --autogenerate -m "add user table"`
3. **Apply the migration**: `bash scripts/migrate.sh`
4. **Create DTOs** in `app/dtos/` for request/response validation
5. **Create service** in `app/services/` for business logic
6. **Create router** in `app/routers/` with your endpoints
7. **Register router** in `app/routers/routes.py`
8. **Write tests** in `test/`

<!-- TOC --><a name="database-migrations"></a>

### Database migrations

```bash
# Create a migration after changing models
uv run alembic revision --autogenerate -m "description of changes"

# Apply migrations to development database
bash scripts/migrate.sh

# Apply migrations to test database
bash scripts/migrate.sh --testing

# Reset database (drop, recreate, and migrate)
bash scripts/reset_db.sh

# Reset test database
bash scripts/reset_db.sh --testing

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
uv run pytest test/test_health.py

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
docker build -t {{APP-NAME}} .

# Run container
docker run -p 8000:8000 {{APP-NAME}}

# Or use Docker Compose
docker-compose up
```

<!-- TOC --><a name="environment-variables"></a>

## Environment Variables

See [`.env.example`](./.env.example) for all required environment variables. Copy it to `.env` and adjust values as needed.
