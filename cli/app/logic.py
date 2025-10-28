from pathlib import Path
import shutil
import subprocess
from typing import NamedTuple

REPO_URL = "https://github.com/SenZmaKi/create-fastapi-app.git"


class AppConfig(NamedTuple):
    name: str
    description: str
    setup_database: bool
    initialize_git: bool


class CloneError(Exception):
    pass


def clone_repo(config: AppConfig) -> None:
    result = subprocess.run(
        ["git", "clone", REPO_URL, config.name],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error_msg = result.stderr.strip() if result.stderr else "Unknown error"
        raise CloneError(f"Failed to clone repository: {error_msg}")


def apply_config(repo_dir: Path, config: AppConfig) -> None:
    for file in repo_dir.rglob("*"):
        if file.is_file():
            content = file.read_text()
            content = content.replace("{{APP_NAME}}", config.name)
            content = content.replace("{{APP_DESCRIPTION}}", config.description)
            file.write_text(content)


def initialize_repo(repo_dir: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )


def configure_app(
    config: AppConfig,
    repo_dir: Path,
) -> None:
    shutil.rmtree(repo_dir / ".git")
    shutil.rmtree(repo_dir / "cli")
    template_dir = repo_dir / "template"
    shutil.move(template_dir, repo_dir)
    shutil.move(repo_dir / ".env.example", repo_dir / ".env")
    apply_config(repo_dir, config)
