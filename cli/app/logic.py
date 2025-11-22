from pathlib import Path
import shutil
import subprocess
from typing import NamedTuple
import uuid

REPO_URL = "https://github.com/SenZmaKi/create-fastapi-app.git"


class AppConfig(NamedTuple):
    name: str
    description: str
    setup_database: bool
    initialize_git: bool


class CommandError(Exception):
    message = "Command failed"

    def __init__(self, stderr: str) -> None:
        super().__init__(f"{self.message}: {stderr}")


class CloneError(CommandError):
    message = "Failed to clone repository"


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


def clone_repo(config: AppConfig) -> Path:
    def get_repo_dir() -> Path:
        repo_dir = Path.cwd() / f"{config.name}-temp-{uuid.uuid4().hex[:8]}"
        if repo_dir.exists():
            return get_repo_dir()
        return repo_dir

    repo_dir = get_repo_dir()

    run_process(
        ["git", "clone", REPO_URL, str(repo_dir)],
        CloneError,
    )
    return repo_dir


def apply_config(app_dir: Path, config: AppConfig) -> None:
    for file in app_dir.rglob("*"):
        if file.is_file():
            content = file.read_text()
            content = content.replace("{{APP-NAME}}", config.name)
            content = content.replace("{{APP-DESCRIPTION}}", config.description)
            file.write_text(content)


def configure_app_dir(
    cwd: Path,
    config: AppConfig,
    repo_dir: Path,
) -> Path:
    template_dir = repo_dir / "template"
    app_dir = cwd / config.name
    if app_dir.exists() and next(app_dir.glob("*"), None):
        raise FileExistsError(
            f"The directory '{app_dir}' already exists and is not empty."
        )
    shutil.move(template_dir, app_dir)
    shutil.move(app_dir / ".env.example", app_dir / ".env")
    shutil.rmtree(repo_dir)
    apply_config(app_dir, config)
    return app_dir


def install_dependencies(app_dir: Path) -> None:
    run_process(
        ["uv", "sync"],
        InstallError,
        cwd=app_dir,
    )


def setup_database(app_dir: Path) -> None:
    run_process(
        ["uv", "run", "python", "-m", "scripts.setup_db"],
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
