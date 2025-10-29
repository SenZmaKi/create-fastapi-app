import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import questionary
from questionary import Style

from app.logic import (
    AppConfig,
    clone_repo,
    configure_app_dir,
    REPO_URL,
    init_git_repo,
    install_dependencies,
    setup_database,
)

VERSION = "v0.1.0"
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
    header = Text(f"Create FastAPI App {VERSION}", style="bold cyan")
    console.print(Panel(header, border_style="cyan"))
    console.print()


def print_footer() -> None:
    footer = (
        Text("Made with ", style="dim")
        + Text("❤️ ", style="red")
        + Text(" by ", style="dim")
        + Text("SenZmaKi", style="dim link https://github.com/SenZmaKi/")
    )
    console.print(footer, justify="center")
    console.print()


def get_user_input() -> AppConfig:
    app_name = questionary.text(
        "What is your app's name?",
        style=custom_style,
        validate=lambda text: True if text.strip() else "App name cannot be empty",
    ).ask()

    if not app_name:
        console.print("[red]✗[/red] Operation cancelled.")
        sys.exit(0)

    app_description = questionary.text("App description:", style=custom_style).ask()

    if app_description is None:
        console.print("[red]✗[/red] Operation cancelled.")
        sys.exit(0)

    if not app_description.strip():
        app_description = "A FastAPI application"

    setup_database = questionary.confirm(
        "Setup database?", default=True, style=custom_style
    ).ask()

    if setup_database is None:
        console.print("[red]✗[/red] Operation cancelled.")
        sys.exit(0)

    initialize_git = questionary.confirm(
        "Initialize a git repository?", default=True, style=custom_style
    ).ask()

    if initialize_git is None:
        console.print("[red]✗[/red] Operation cancelled.")
        sys.exit(0)

    return AppConfig(
        name=app_name.strip(),
        description=app_description.strip(),
        setup_database=setup_database,
        initialize_git=initialize_git,
    )


def setup_app(config: AppConfig) -> Path:
    console.print()
    console.print(f"[cyan]Creating {config.name}...[/cyan]")
    console.print()

    try:
        with Progress(
            CompletableSpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            current_task = progress.add_task(
                f"Cloning repository from {REPO_URL}...", total=None
            )
            repo_dir = clone_repo(config)
            progress.update(
                current_task,
                description=f"Cloned repository from {REPO_URL}",
                completed=1,
                total=1,
            )

            current_task = progress.add_task("Applying configuration...", total=None)
            app_dir = configure_app_dir(Path.cwd(), config, repo_dir)
            progress.update(
                current_task, description="Applied configuration", completed=1, total=1
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
    commands = f"[bold]To get started:[/bold]\n  [cyan]cd {config.name}[/cyan]\n"
    if not config.setup_database:
        commands += "  [cyan]uv run python -m scripts.setup_db[/cyan]\n"
    commands += "  [cyan]uv run python -m app[/cyan]"

    console.print(
        Panel(
            f"[green bold]Success![/green bold]\n\n"
            f"Created [cyan]{config.name}[/cyan] at [dim]{repo_dir}[/dim]\n\n"
            f"{commands}",
            title="[green]✓[/green] Done",
            border_style="green",
        )
    )
    console.print()


def run_ui() -> None:
    print_header()
    config = get_user_input()
    app_dir = setup_app(config)
    print_to_get_started_commands(app_dir, config)
    print_footer()
