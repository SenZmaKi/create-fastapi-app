<!-- TOC --><a name="create-fastapi-app"></a>

# Create-FastAPI-App

A CLI tool to quickly scaffold production-ready FastAPI applications with a well-structured project template.

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

## Table of Contents

- [Create-FastAPI-App](#create-fastapi-app)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [What's Included](#whats-included)
  - [Generated Project Structure](#generated-project-structure)
  - [CLI Options](#cli-options)
  - [Development](#development)
  - [TODO](#todo)
  - [License](#license)
  - [Contributing](#contributing)

<!-- TOC end -->

<!-- TOC --><a name="features"></a>

## Features

- 🚀 **Interactive CLI** - User-friendly prompts for project configuration
- 📦 **Pre-configured Template** - Production-ready FastAPI application with best practices
- 🗄️ **Database Ready** - PostgreSQL integration with SQLAlchemy and Alembic migrations
- 🔒 **Type-Safe** - Full type checking with Pyright and Pydantic settings
- 🐳 **Docker Support** - Containerization ready with Dockerfile and docker-compose
- ✅ **Testing Setup** - Configured pytest with coverage support
- 🎨 **Code Quality** - Pre-commit hooks with Ruff for linting and formatting
- 🔧 **Developer Tools** - Helper scripts for database setup and migrations

<!-- TOC --><a name="requirements"></a>

## Requirements

- **uv** - Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git** - Version control
- **PostgreSQL** - For database integration (optional, can be configured later)

<!-- TOC --><a name="installation"></a>

## Installation

### Using uvx (Recommended)

Run directly without installation:

```bash
uvx git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

### Using uv

Install globally:

```bash
uv tool install git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

### Using pip

```bash
pip install git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

<!-- TOC --><a name="usage"></a>

## Usage

The CLI can be run directly without installation using `uvx`:

```bash
uvx git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

Or install it globally:

```bash
uv tool install git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

<!-- TOC --><a name="usage"></a>

## Usage

Run the CLI to create a new FastAPI project:

```bash
uvx git+https://github.com/senzmaki/create-fastapi-app.git#subdirectory=cli
```

The interactive CLI will guide you through the setup process:

1. **Project Name** - Enter your application name (e.g., `my-awesome-api`)
2. **Project Description** - Provide a brief description
3. **Git Repository** - Choose whether to initialize a git repository with an initial commit
4. **Database Setup** - Optionally set up the PostgreSQL database and run initial migrations

After completion, your project will be ready with:

- All dependencies installed
- Database configured (if selected)
- Git repository initialized (if selected)
- Ready to run with `uv run python -m app`

<!-- TOC --><a name="whats-included"></a>

## What's Included

The generated project comes with:

- ⚡ **FastAPI Application** - Modern async web framework with automatic API documentation
- 🗄️ **SQLAlchemy + Alembic** - Async ORM and database migration management
- 🔧 **Helper Scripts** - Database setup, migration, and development server utilities
- 🧪 **Testing Framework** - Pytest with async support and example tests
- 📝 **Type Checking** - Pyright configuration for full type safety
- 🎨 **Code Formatting** - Ruff for fast linting and formatting
- 🔗 **Pre-commit Hooks** - Automated code quality checks
- 🐳 **Docker Ready** - Dockerfile and docker-compose configuration
- 📚 **Comprehensive Documentation** - Detailed README with project structure and workflows
- ⚙️ **Environment Management** - Type-safe settings with Pydantic

<!-- TOC --><a name="generated-project-structure"></a>

## Generated Project Structure

```
your-project-name/
├── alembic/                 # Database migrations
│   ├── versions/            # Migration files
│   └── env.py              # Alembic configuration
├── app/                     # Main application code
│   ├── database/            # Database session management
│   ├── dtos/                # Pydantic schemas for request/response
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic layer
│   ├── utils/               # Utilities (settings, logging, errors)
│   └── main.py              # FastAPI app factory
├── scripts/                 # Development and database management scripts
│   ├── start_server.sh      # Start server
│   ├── setup_db.sh          # Database initialization
│   ├── reset_db.sh          # Drop and recreate database
│   ├── migrate.sh           # Run database migrations
│   ├── test.sh              # Run test suite
│   ├── utils.sh             # Shared script utilities
│   ├── db/                  # Database Python modules
│   │   ├── setup.py         # Database creation logic
│   │   └── drop.py          # Database drop logic
│   └── utils/               # Script utilities
├── test/                    # Test suite
│   └── test_health.py       # Example tests
├── alembic.ini              # Alembic configuration
├── conftest.py              # Pytest fixtures
├── docker-compose.yml       # Docker Compose setup
├── Dockerfile               # Container configuration
├── pyproject.toml           # Project dependencies and metadata
├── pyrightconfig.json       # Type checker settings
├── pytest.ini               # Pytest configuration
└── README.md                # Project documentation
```

For detailed information about each directory and file, see the generated project's [README.md](./template/README.md).

<!-- TOC --><a name="cli-options"></a>

## CLI Options

The CLI currently runs in interactive mode and prompts for:

| Prompt                  | Description                                                                             | Required          |
| ----------------------- | --------------------------------------------------------------------------------------- | ----------------- |
| **Project Name**        | The name of your FastAPI application (will be used for directory name and package name) | Yes               |
| **Project Description** | A brief description of your application                                                 | Yes               |
| **Initialize Git**      | Whether to initialize a git repository and create an initial commit                     | No (default: Yes) |
| **Setup Database**      | Whether to create the PostgreSQL database and run initial migrations                    | No (default: Yes) |

<!-- TOC --><a name="development"></a>

## Development

To contribute to the CLI tool itself:

1. Clone the repository:

```bash
git clone https://github.com/senzmaki/create-fastapi-app.git
cd create-fastapi-app
```

2. Install development dependencies:

```bash
cd cli
uv sync
```

3. Make your changes and test locally:

```bash
uv run python -m app
```

<!-- TOC --><a name="todo"></a>

## TODO

- Fix reload includes and excludes not working.

<!-- TOC --><a name="license"></a>

## License

MIT

<!-- TOC --><a name="contributing"></a>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
