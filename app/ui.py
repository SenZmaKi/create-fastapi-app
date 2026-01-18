import shutil
import sys
import re
import keyword
from pathlib import Path
from typing import Any, Callable
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import questionary
from questionary import Style
from app.logic import (
    AppConfig,
    copy_template,
    init_git_repo,
    install_dependencies,
    setup_database,
    assert_has_prerequisites,
    PrerequisiteError,
    PostgreSQLNotRunningError,
)

VERSION = "0.1.0"
console = Console()


class CompletableSpinnerColumn(SpinnerColumn):
    """A spinner column that shows a checkmark when task is finished."""

    def render(self, task):
        if task.finished:
            return Text("✓", style="green")
        return super().render(task)


custom_style = Style(
    [
        ("question", "bold"),
        ("answer", "fg:#00aa00 bold"),
        ("pointer", "fg:#00aa00 bold"),
        ("highlighted", "fg:#00aa00 bold"),
        ("selected", "fg:#00aa00"),
        ("separator", "fg:#6c6c6c"),
        ("instruction", "fg:#858585"),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]
)


def print_header() -> None:
    console.print()
    header = Text(f"Create FastAPI App v{VERSION}", style="bold cyan")
    console.print(Panel(header, border_style="cyan"))
    console.print()


def print_footer() -> None:
    footer = (
        Text("Made with ", style="dim")
        + Text("❤️ ", style="red")
        + Text(" by ", style="dim")
        + Text("SenZmaKi", style="link https://github.com/SenZmaKi/")
    )
    console.print(footer, justify="center")
    console.print()


def validate_app_name(name: str) -> bool | str:
    """Validate app name for Python package naming conventions."""
    name = name.strip()
    if not name:
        return "App name cannot be empty"
    if keyword.iskeyword(name):
        return f"'{name}' is a Python keyword and cannot be used as app name"
    if not re.match(r"^[a-z][a-z0-9-]*$", name):
        return "App name must only contain lowercase letters, numbers, and hyphens"
    return True


def ask(asker: Callable[[], Any]) -> Any:
    answer = asker()
    if answer is None:
        sys.exit(0)
    return answer


def get_user_input() -> AppConfig:
    app_name = ask(
        questionary.text(
            "What is your app's name?",
            style=custom_style,
            validate=validate_app_name,
        ).ask
    )

    app_name_ui = ask(
        questionary.text(
            "What name should appear for your app across the UI?",
            style=custom_style,
            validate=lambda text: True
            if text.strip()
            else "App name ui cannot be empty",
        ).ask
    )

    app_description = ask(
        questionary.text(
            "App description:",
            style=custom_style,
            default="A FastAPI application",
        ).ask
    )

    setup_database = ask(
        questionary.confirm("Setup database?", default=True, style=custom_style).ask
    )

    initialize_git = ask(
        questionary.confirm(
            "Initialize a git repository?", default=True, style=custom_style
        ).ask
    )

    enable_docker = ask(
        questionary.confirm(
            "Enable Docker integration?", default=True, style=custom_style
        ).ask
    )

    enable_auth = ask(
        questionary.confirm(
            "Enable authentication system?", default=True, style=custom_style
        ).ask
    )

    enable_soft_delete = ask(
        questionary.confirm(
            "Enable soft delete for models?", default=True, style=custom_style
        ).ask
    )

    enable_vps_deployment = ask(
        questionary.confirm(
            "Enable VPS deployment configuration?", default=True, style=custom_style
        ).ask
    )

    return AppConfig(
        name=app_name.strip(),
        name_ui=app_name_ui.strip(),
        description=app_description.strip(),
        setup_database=setup_database,
        initialize_git=initialize_git,
        enable_docker=enable_docker,
        enable_auth=enable_auth,
        enable_soft_delete=enable_soft_delete,
        enable_vps_deployment=enable_vps_deployment,
    )


# TODO: Rollback database setup if error occurs after that step
def rollback_setup_app(app_dir: Path | None) -> None:
    try:
        if app_dir and app_dir.exists():
            shutil.rmtree(app_dir)
    except Exception:
        pass


def setup_app(config: AppConfig) -> Path:
    console.print()
    console.print(f"[cyan]Creating {config.name}...[/cyan]")
    console.print()

    # Check prerequisites before starting
    try:
        assert_has_prerequisites(config)
    except PrerequisiteError as e:
        console.print(f"[red]✗[/red] {e.tool_name} is not installed.")
        console.print(
            f"Please install it from [link={e.installation_url}]{e.installation_url}[/link] and try again."
        )
        sys.exit(1)
    except PostgreSQLNotRunningError:
        console.print("[red]✗[/red] PostgreSQL is not running.")
        console.print(
            "Please start PostgreSQL and try again. You can find instructions at [link=https://www.postgresql.org/docs/current/server-start.html]https://www.postgresql.org/docs/current/server-start.html[/link]"
        )
        sys.exit(1)

    app_dir: Path | None = None

    try:
        with Progress(
            CompletableSpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            current_task = progress.add_task("Copying template...", total=None)
            app_dir = copy_template(config)
            progress.update(
                current_task,
                description="Copied template",
                completed=1,
                total=1,
            )

            current_task = progress.add_task("Installing dependencies...", total=None)
            install_dependencies(app_dir)
            progress.update(
                current_task, description="Installed dependencies", completed=1, total=1
            )

            if config.setup_database:
                current_task = progress.add_task("Setting up database...", total=None)
                setup_database(app_dir)
                progress.update(
                    current_task, description="Set up database", completed=1, total=1
                )

            if config.initialize_git:
                current_task = progress.add_task(
                    "Initializing git repository...", total=None
                )
                init_git_repo(app_dir)
                progress.update(
                    current_task,
                    description="Initialized git repository",
                    completed=1,
                    total=1,
                )

        console.print()
        return app_dir

    except Exception as e:
        rollback_setup_app(app_dir)
        console.print()
        console.print(
            Panel(
                f"[red bold]Error:[/red bold]\n{str(e)}",
                title="[red]✗[/red] Failed",
                border_style="red",
            )
        )
        console.print()
        sys.exit(1)


def print_to_get_started_commands(repo_dir: Path, config: AppConfig) -> None:
    console.print("[green bold]✓ Success![/green bold]\n")
    console.print(f"Created [cyan]{config.name}[/cyan] at [dim]{repo_dir}[/dim]\n")
    console.print("[bold]To get started:[/bold]\n")
    console.print(f"  [cyan]cd {config.name}[/cyan]")
    if not config.setup_database:
        console.print("  [cyan]scripts/create_db.sh[/cyan]")
        console.print(
            "  [cyan]uv run alembic revision --autogenerate -m 'Initial migration'[/cyan]"
        )
        console.print("  [cyan]scripts/migrate_db.sh[/cyan]")
        if config.initialize_git:
            console.print("  [cyan]git add .[/cyan]")
            console.print("  [cyan]git commit -m 'Add initial migration'[/cyan]")
    console.print("  [cyan]scripts/start_server.sh[/cyan]")
    console.print()


def run_ui() -> None:
    print_header()
    config = get_user_input()
    app_dir = setup_app(config)
    print_to_get_started_commands(app_dir, config)
    print_footer()
