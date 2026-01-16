import sys
from app.utils.settings import settings
from scripts.utils.utils import print_colored
from scripts.db.utils.utils import (
    check_postgresql,
    check_postgresql_running,
    get_db_info,
    DBInfo,
    get_env,
)
import subprocess


def drop_database(db_info: DBInfo) -> bool:
    print_colored(f"\nDropping database '{db_info.name}'...")

    try:
        # Use dropdb command
        env = get_env(db_info)
        subprocess.run(
            [
                "dropdb",
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
        print_colored(f"✓ Database '{db_info.name}' dropped successfully!", "green")
        return True
    except subprocess.CalledProcessError as e:
        e_stderr = str(e.stderr)
        if "does not exist" in e_stderr:
            print_colored(f"Database '{db_info.name}' does not exist.", "blue")
            return True
        else:
            print_colored("✗ Failed to drop database:", "red")
            print(e_stderr)
            return False


def main() -> int:
    print("================================")
    print("💣  Database Teardown")
    print("================================")
    print(f"\nEnvironment: {settings.deployment_environment}")

    db_info = get_db_info()
    print(db_info)
    if "--yes" not in sys.argv and "-y" not in sys.argv:
        response = input("Are you sure you want to drop the database? (y/n): ")
        if response.lower() != "y":
            print_colored("Database teardown cancelled.", "blue")
            return 0

    # Check PostgreSQL installation
    if not check_postgresql():
        return 1

    # Check if PostgreSQL is running
    if not check_postgresql_running(db_info.host, db_info.port):
        return 1

    # Drop database
    if not drop_database(db_info):
        return 1

    # Success message
    print_colored("\n================================", "green")
    print_colored("Database teardown completed!", "green")
    print_colored("================================", "green")

    return 0


if __name__ == "__main__":
    sys.exit(main())
