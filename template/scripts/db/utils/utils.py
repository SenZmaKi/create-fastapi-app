import os
import subprocess
from typing import NamedTuple
from urllib.parse import urlparse
from app.utils.error import ConfigError
from scripts.utils.utils import print_colored
from app.utils.settings import settings


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
    name: str

    url: str

    def __str__(self) -> str:
        return f"""
Name: {self.name}
Host: {self.host}:{self.port}
User: {self.user}
URL: {self.url}
"""


def get_db_info() -> DBInfo:
    """Get database info from environment variables."""
    database_url = settings.get_database_url()
    return parse_database_url(database_url)


def parse_database_url(database_url: str) -> DBInfo:
    """Parse database URL into components."""
    parsed = urlparse(database_url)

    # Remove the +asyncpg suffix for connection purposes
    scheme = parsed.scheme.replace("+asyncpg", "")
    if not parsed.port:
        raise ConfigError("Database URL must include a port number.")
    if not parsed.path:
        raise ConfigError("Database URL must include a database name.")
    database = parsed.path.lstrip("/")
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
        name=database,
        url=database_url,
    )


def get_env(db_info: DBInfo) -> dict[str, str]:
    env = os.environ.copy()
    if db_info.password:
        env["PGPASSWORD"] = db_info.password
    return env
