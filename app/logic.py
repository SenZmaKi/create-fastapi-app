from pathlib import Path
import subprocess
import shutil
from typing import NamedTuple
from copier import run_copy
from rich.console import Console

TEMPLATE_DIR = Path(__file__).parent / "template"
console = Console()


class AppConfig(NamedTuple):
    name: str
    name_ui: str
    description: str
    setup_database: bool
    initialize_git: bool
    enable_docker: bool
    enable_auth: bool
    enable_soft_delete: bool
    enable_vps_deployment: bool


class CommandError(Exception):
    message = "Command failed"

    def __init__(self, stderr: str, command: str) -> None:
        super().__init__(f"{self.message} ({command}): {stderr}")


class CopyTemplateError(Exception):
    message = "Failed to copy template"


class InstallError(CommandError):
    message = "Failed to install dependencies"


class SetupDatabaseError(CommandError):
    message = "Failed to set up database"


class InitGitRepoError(CommandError):
    message = "Failed to initialize git repository"


class PrerequisiteError(Exception):
    """Raised when required tools are not installed"""

    def __init__(self, tool_name: str, installation_url: str) -> None:
        self.tool_name = tool_name
        self.installation_url = installation_url
        super().__init__(f"{tool_name} is not installed.")


class PostgreSQLNotRunningError(Exception):
    pass


def is_postgresql_running(host: str = "localhost", port: int = 5432) -> bool:
    try:
        subprocess.run(
            ["pg_isready", "-h", host, "-p", str(port)],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def assert_has_prerequisites(config: AppConfig) -> None:
    """Assert required tools are installed before starting setup."""

    # uv is always required for dependency installation
    if not shutil.which("uv"):
        raise PrerequisiteError(
            tool_name="uv", installation_url="https://docs.astral.sh/uv/"
        )
    if not shutil.which("git"):
        raise PrerequisiteError(
            tool_name="Git", installation_url="https://git-scm.com/downloads"
        )

    # Check PostgreSQL if database setup is requested
    if config.setup_database:
        if not shutil.which("pg_isready"):
            raise PrerequisiteError(
                tool_name="PostgreSQL",
                installation_url="https://www.postgresql.org/download/",
            )

        if not is_postgresql_running():
            raise PostgreSQLNotRunningError()


def run_process(
    command: list[str],
    command_exception: type[CommandError],
    cwd: Path | None = None,
) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise command_exception(stderr=result.stderr, command=" ".join(command))


def copy_template(config: AppConfig) -> Path:
    """Copy and configure template using Copier."""
    app_dir = Path.cwd() / config.name

    if app_dir.exists() and next(app_dir.glob("*"), None):
        raise FileExistsError(
            f"The directory '{app_dir}' already exists and is not empty."
        )

    try:
        # Prepare Copier data
        data = {
            "app_name": config.name,
            "app_name_ui": config.name_ui,
            "app_description": config.description,
            "enable_docker": config.enable_docker,
            "enable_auth": config.enable_auth,
            "enable_soft_delete": config.enable_soft_delete,
            "enable_vps_deployment": config.enable_vps_deployment,
        }

        # Run copier
        run_copy(
            src_path=str(TEMPLATE_DIR),
            dst_path=str(app_dir),
            data=data,
            quiet=True,
        )

        return app_dir
    except Exception as e:
        raise CopyTemplateError(str(e))


def install_dependencies(app_dir: Path) -> None:
    run_process(
        ["uv", "sync"],
        InstallError,
        cwd=app_dir,
    )


def setup_database(app_dir: Path) -> None:
    run_process(
        ["uv", "run", "python", "-m", "scripts.db.create"],
        SetupDatabaseError,
        cwd=app_dir,
    )
    run_process(
        ["uv", "run", "alembic", "revision", "-m", "Initial migration"],
        SetupDatabaseError,
        cwd=app_dir,
    )
    run_process(
        ["uv", "run", "python", "-m", "alembic", "upgrade", "head"],
        SetupDatabaseError,
        cwd=app_dir,
    )


def init_git_repo(app_dir: Path) -> None:
    return
    run_process(["git", "init"], InitGitRepoError, cwd=app_dir)
    run_process(["uv", "run", "pre-commit", "install"], InitGitRepoError, cwd=app_dir)
    run_process(["git", "add", "."], InitGitRepoError, cwd=app_dir)
    run_process(
        ["git", "commit", "-m", "Initial commit"],
        InitGitRepoError,
        cwd=app_dir,
    )
