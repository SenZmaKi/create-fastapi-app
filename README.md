# Create FastAPI App

A CLI tool for scaffolding production-ready FastAPI applications with best practices and common features pre-configured.

## Table of Contents

- [Create FastAPI App](#create-fastapi-app)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Configuration Options](#configuration-options)
  - [What Gets Generated](#what-gets-generated)

## Installation

Run directly without installation using uvx:

```bash
uvx git+https://github.com/senzmaki/create-fastapi-app.git
```

Or install globally:

```bash
uv tool install git+https://github.com/senzmaki/create-fastapi-app.git
```

Then run:

```bash
create-fastapi-app
```

## Prerequisites

The following tools must be installed before using create-fastapi-app:

- [Git](https://git-scm.com/downloads) - Version control system
- [uv](https://docs.astral.sh/uv/) - Python package manager
- [PostgreSQL](https://www.postgresql.org/download/) - Database (required if database setup is enabled)

PostgreSQL must be running if you choose to set up the database during project creation.

## Usage

The CLI will guide you through an interactive setup process. You will be prompted to configure the following options:

### Configuration Options

**App name**  
The technical name for your application. Used as the project directory name and Python package name. Must contain only lowercase letters, numbers, and hyphens, and cannot be a Python keyword.

**App name UI**  
The display name for your application. This appears in the generated documentation, API responses, and other user-facing locations.

**App description**  
A brief description of your application. Defaults to "A FastAPI application" if left empty.

**Setup database**  
Default: Yes  
Creates the PostgreSQL database and runs initial migrations. Requires PostgreSQL to be installed and running.

**Initialize git repository**  
Default: Yes  
Initializes a git repository, installs pre-commit hooks, formats the code, and creates an initial commit.

**Enable Docker integration**  
Default: Yes  
Includes Docker configuration files and Docker Compose setup.

**Enable authentication system**  
Default: Yes  
Adds a complete user authentication system with email verification, password reset, and session management.

**Enable soft delete for models**  
Default: Yes  
Implements soft delete functionality, allowing records to be marked as deleted without permanent removal from the database.

**Enable VPS deployment configuration**  
Default: Yes  
Includes PM2 configuration for process management and GitHub Actions workflows for automated deployment to Virtual Private Servers.

## What Gets Generated

The tool creates a fully configured FastAPI project with:

- FastAPI application with automatic API documentation
- PostgreSQL database with SQLAlchemy ORM and Alembic migrations
- Type safety with Pyright and Pydantic
- Structured logging with request correlation IDs
- Security middlewares (rate limiting, CORS, DocShield)
- Pytest testing setup with parallel execution
- Pre-commit hooks with Ruff formatter and linter
- Environment configuration with .env support
- Development and production scripts

Optional features based on your selections:

- Docker containerization with optimized images
- User authentication with email verification
- Soft delete capability for database models
- VPS deployment with PM2 and CI/CD workflows
