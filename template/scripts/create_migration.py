import subprocess
import sys
from scripts.utils import print_colored


def main() -> int:
    print("================================")
    print("Creating Initial Migration")
    print("================================")

    print_colored("Generating initial migration...", "blue")
    try:
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "initial_schema"],
            capture_output=True,
            text=True,
        )
        print_colored("✓ Migration created successfully!", "green")
        print_colored("To apply the migration, run:", "blue")
        print_colored("  alembic upgrade head")
        return 0
    except subprocess.CalledProcessError:
        print("✗ Failed to create migration:", "red")
        print(sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
