#!/usr/bin/env python3
import sys
import os
import subprocess
from typing import NamedTuple
from urllib.parse import urlparse
from app.utils.error import ConfigError
from app.utils.settings import settings
from scripts.utils import print_colored


def check_postgresql() -> bool:
    """Check if PostgreSQL is installed and running."""
    # Check if psql is installed
    try:
        subprocess.run(
            ["psql", "--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("PostgreSQL is not installed!", "red")
        print("Please install PostgreSQL first:")
        print("  macOS: brew install postgresql@14")
        print("  Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False

    return True


def check_postgresql_running(host: str, port: int) -> bool:
    """Check if PostgreSQL is running."""
    try:
        subprocess.run(
            ["pg_isready", "-h", host, "-p", str(port)],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        print_colored("PostgreSQL is not running!", "red")
        print("Please start PostgreSQL first:")
        print("  macOS: brew services start postgresql@18")
        print("  Ubuntu: sudo service postgresql start")
        return False


class DBInfo(NamedTuple):
    scheme: str
    user: str
    password: str
    host: str
    port: int
    database: str


def parse_database_url(database_url: str) -> DBInfo:
    """Parse database URL into components."""
    parsed = urlparse(database_url)

    # Remove the +asyncpg suffix for connection purposes
    scheme = parsed.scheme.replace("+asyncpg", "")
    if not parsed.port:
        raise ConfigError("Database URL must include a port number.")
    if not parsed.path:
        raise ConfigError("Database URL must include a database name.")
    database = parsed.path.lstrip("/") if parsed.path else "igad"
    if not database:
        raise ConfigError("Database URL must include a database name.")
    if not parsed.username:
        raise ConfigError("Database URL must include a username.")
    if not parsed.hostname:
        raise ConfigError("Database URL must include a hostname.")
    if not parsed.password:
        raise ConfigError("Database URL must include a password.")

    return DBInfo(
        scheme=scheme,
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port,
        database=database,
    )


def create_database(db_info: DBInfo) -> bool:
    print_colored(f"\nCreating database '{db_info.database}'...")

    try:
        # Use createdb command
        env = os.environ.copy()
        if db_info.password:
            env["PGPASSWORD"] = db_info.password

        subprocess.run(
            [
                "createdb",
                "-h",
                db_info.host,
                "-p",
                str(db_info.port),
                "-U",
                db_info.user,
                db_info.database,
            ],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        print_colored(f"✓ Database '{db_info.database}' created successfully!", "green")
        return True
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e.stderr):
            print_colored(f"Database '{db_info.database}' already exists.", "blue")
            return True
        else:
            print_colored("✗ Failed to create database:", "red")
            print(sys.stderr)
            return False


def run_migrations(database_url: str) -> bool:
    print_colored("\nRunning database migrations...")

    if not os.path.exists("alembic.ini"):
        print_colored("No alembic.ini found. Skipping migrations.", "blue")
        print_colored("Tables will be created automatically on first run.", "blue")
        return True

    try:
        env = os.environ.copy()
        env["DATABASE_URL"] = database_url

        subprocess.run(
            ["alembic", "upgrade", "head"],
            env=env,
            check=True,
        )
        print_colored("✓ Migrations completed successfully!", "green")
        return True
    except subprocess.CalledProcessError:
        print_colored("✗ Migration failed!", "red")
        return False


def main() -> int:
    """Main function."""
    print("================================")
    print("Database Setup")
    print("================================")
    print(f"\nEnvironment: {settings.env}")

    # Get database URL based on environment
    database_url = settings.get_database_url()
    db_info = parse_database_url(database_url)

    print(f"Database: {db_info.database}")
    print(f"Host: {db_info.host}:{db_info.port}")
    print(f"User: {db_info.user}")

    # Check PostgreSQL installation
    if not check_postgresql():
        return 1

    # Check if PostgreSQL is running
    if not check_postgresql_running(db_info.host, db_info.port):
        return 1

    # Create database
    if not create_database(db_info):
        return 1

    # Run migrations
    if not run_migrations(database_url):
        return 1

    # Success message
    print_colored("\n================================", "green")
    print_colored("Database setup completed!", "green")
    print_colored("================================", "green")
    print("\nDatabase connection string:")
    print_colored(database_url, "blue")

    return 0


if __name__ == "__main__":
    sys.exit(main())
