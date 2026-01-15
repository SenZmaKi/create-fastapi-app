from pathlib import Path
import subprocess
from typing import NamedTuple
from copier import run_copy

TEMPLATE_DIR = Path(__file__).parent / "template"


class AppConfig(NamedTuple):
    name: str
    description: str
    setup_database: bool
    initialize_git: bool
    enable_docker: bool
    enable_auth: bool
    enable_soft_delete: bool
    enable_vps_deployment: bool


class CommandError(Exception):
    message = "Command failed"

    def __init__(self, stderr: str) -> None:
        super().__init__(f"{self.message}: {stderr}")


class CopyTemplateError(CommandError):
    message = "Failed to copy template"


class InstallError(CommandError):
    message = "Failed to install dependencies"


class SetupDatabaseError(CommandError):
    message = "Failed to set up database"


class InitGitRepoError(CommandError):
    message = "Failed to initialize git repository"


def run_process(
    command: list[str],
    command_exception: type[CommandError],
    cwd: Path | None = None,
) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise command_exception(result.stderr)


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
            "app_description": config.description,
            "setup_database": config.setup_database,
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
            unsafe=True,
            quiet=True,
        )

        # Post-process: Remove conditional files that Copier didn't exclude
        # This is a workaround since Copier's _exclude with Jinja doesn't always work reliably
        if not config.enable_auth:
            auth_files = [
                app_dir / "app" / "services" / "auth.py",
                app_dir / "app" / "services" / "email.py",
                app_dir / "app" / "services" / "scheduler.py",
                app_dir / "app" / "routers" / "auth.py",
                app_dir / "app" / "routers" / "utils" / "auth.py",
                app_dir / "app" / "dtos" / "auth.py",
                app_dir / "app" / "models" / "auth.py",
            ]
            for file in auth_files:
                if file.exists():
                    file.unlink()

            # Remove utils directory if it's empty
            utils_dir = app_dir / "app" / "routers" / "utils"
            if utils_dir.exists() and not any(utils_dir.iterdir()):
                utils_dir.rmdir()

        if not config.enable_docker:
            docker_files = [
                app_dir / "Dockerfile",
                app_dir / ".dockerignore",
                app_dir / "docker-compose.yml",
                app_dir / ".github" / "workflows" / "docker.yml",
            ]
            for file in docker_files:
                if file.exists():
                    file.unlink()

        if not config.enable_vps_deployment:
            pm2_file = app_dir / "pm2.config.js"
            if pm2_file.exists():
                pm2_file.unlink()

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
        ["uv", "run", "python", "-m", "scripts.create_db"],
        SetupDatabaseError,
        cwd=app_dir,
    )
    run_process(
        ["uv", "run", "python", "-m", "alembic", "upgrade", "head"],
        SetupDatabaseError,
        cwd=app_dir,
    )


def init_git_repo(app_dir: Path) -> None:
    run_process(["git", "init"], InitGitRepoError, cwd=app_dir)
    run_process(["uv", "run", "pre-commit", "install"], InitGitRepoError, cwd=app_dir)
    run_process(["uv", "run", "ruff", "format", "."], InitGitRepoError, cwd=app_dir)
    run_process(["git", "add", "."], InitGitRepoError, cwd=app_dir)
    run_process(
        ["git", "commit", "-m", "Initial commit"],
        InitGitRepoError,
        cwd=app_dir,
    )
