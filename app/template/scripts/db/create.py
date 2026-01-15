#!/usr/bin/env python3
import sys
import subprocess
from app.utils.settings import settings
from scripts.utils.utils import print_colored
from scripts.db.utils.utils import (
    check_postgresql,
    check_postgresql_running,
    get_db_info,
    DBInfo,
    get_env,
)


def create_database(db_info: DBInfo) -> bool:
    print_colored(f"\nCreating database '{db_info.name}'...")

    try:
        # Use createdb command
        env = get_env(db_info)
        subprocess.run(
            [
                "createdb",
                "-h",
                db_info.host,
                "-p",
                str(db_info.port),
                "-U",
                db_info.user,
                db_info.name,
            ],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        print_colored(f"✓ Database '{db_info.name}' created successfully!", "green")
        return True
    except subprocess.CalledProcessError as e:
        e_stderr = str(e.stderr)
        if "already exists" in e_stderr:
            print_colored(f"Database '{db_info.name}' already exists.", "blue")
            return True
        else:
            print_colored("✗ Failed to create database:", "red")
            print(e_stderr)
            return False


def main() -> int:
    """Main function."""
    print("================================")
    print("⚒️  Create Database ")
    print("================================")
    print(f"\nEnvironment: {settings.deployment_environment}")

    db_info = get_db_info()
    print(db_info)

    # Check PostgreSQL installation
    if not check_postgresql():
        return 1

    # Check if PostgreSQL is running
    if not check_postgresql_running(db_info.host, db_info.port):
        return 1

    # Create database
    if not create_database(db_info):
        return 1

    # Success message
    print_colored("\n================================", "green")
    print_colored("Database creation completed!", "green")
    print_colored("================================", "green")
    print("\nDatabase connection string:")
    print_colored(db_info.url, "blue")

    return 0


if __name__ == "__main__":
    sys.exit(main())
