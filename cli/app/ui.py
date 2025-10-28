import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import questionary
from questionary import Style

from app.logic import AppConfig, clone_repo, configure_app, REPO_URL

VERSION = "v0.1.0"
console = Console()

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
        + Text("❤️", style="red")
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


def create_app_with_progress(config: AppConfig) -> None:
    console.print()
    console.print(f"[cyan]Creating {config.name}...[/cyan]")
    console.print()

    try:
        repo_dir = Path.cwd() / config.name

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            # Clone repository
            current_task = progress.add_task(
                f"Cloning repository from {REPO_URL}...", total=None
            )
            clone_repo(config)
            progress.update(current_task, completed=True)
            console.print("[green]✓[/green] Repository cloned")

            # Configure app
            current_task = progress.add_task("Cleaning up git history...", total=None)
            progress.update(current_task, completed=True)
            console.print("[green]✓[/green] Cleaned up git history")

            current_task = progress.add_task("Removing CLI directory...", total=None)
            progress.update(current_task, completed=True)
            console.print("[green]✓[/green] Removed CLI directory")

            current_task = progress.add_task(
                "Setting up template structure...", total=None
            )
            progress.update(current_task, completed=True)
            console.print("[green]✓[/green] Template structure ready")

            current_task = progress.add_task(
                "Applying configuration to files...", total=None
            )
            configure_app(config, repo_dir)
            progress.update(current_task, completed=True)
            console.print("[green]✓[/green] Configuration applied")

            # Install dependencies
            current_task = progress.add_task(
                "Installing dependencies with uv sync...", total=None
            )
            result = subprocess.run(
                ["uv", "sync"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise Exception(f"Failed to install dependencies: {result.stderr}")
            progress.update(current_task, completed=True)
            console.print("[green]✓[/green] Dependencies installed")

            # Setup database if requested
            if config.setup_database:
                current_task = progress.add_task("Setting up database...", total=None)
                result = subprocess.run(
                    ["uv", "run", "python", "-m", "scripts.setup_db"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    console.print(
                        f"[yellow]⚠[/yellow] Database setup failed: {result.stderr}"
                    )
                    console.print(
                        "[yellow]You can set it up later by running: uv run python -m scripts.setup_db[/yellow]"
                    )
                else:
                    progress.update(current_task, completed=True)
                    console.print("[green]✓[/green] Database setup completed")

            # Initialize git repository as final step
            if config.initialize_git:
                current_task = progress.add_task(
                    "Initializing git repository...", total=None
                )
                subprocess.run(
                    ["git", "init"], cwd=repo_dir, check=True, capture_output=True
                )
                subprocess.run(
                    ["git", "add", "."], cwd=repo_dir, check=True, capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit"],
                    cwd=repo_dir,
                    check=True,
                    capture_output=True,
                )
                progress.update(current_task, completed=True)
                console.print("[green]✓[/green] Git repository initialized")

        console.print()

        # Build the commands section
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


def run_ui() -> None:
    print_header()
    config = get_user_input()
    create_app_with_progress(config)
    print_footer()
