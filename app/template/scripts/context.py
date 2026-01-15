#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Callable
from gitignore_parser import parse_gitignore


def print_in_stderr(message: str) -> None:
    print(message, file=sys.stderr)


def process_project(
    root_path: Path,
    gitignore_matches: Callable[[Path], bool],
    patterns: list[str],
) -> str:
    """
    Traverses the project root and returns content of files matching the patterns,
    respecting .gitignore rules.
    """
    print_in_stderr(f"--- START: Scanning project for patterns: {patterns} ---")

    combined_output: list[str] = []

    # Iterate through all files in the project
    for file_path in root_path.rglob("*"):
        if not file_path.is_file() or gitignore_matches(file_path):
            continue

        # Check if the file matches any of the provided patterns
        # Patterns can be directories (app/models/*) or extensions (*.py)
        if any(file_path.match(pattern) for pattern in patterns):
            try:
                relative_path = file_path.relative_to(root_path)
                header = f"# FILENAME: {relative_path}\n"
                content = file_path.read_text(encoding="utf-8")
                combined_output.append(header + content.strip())
                print_in_stderr(f"Included: {relative_path}")
            except Exception as e:
                print_in_stderr(f"Error reading {file_path}: {e}")

    print_in_stderr("--- END: Processing complete ---")
    return "\n\n".join(combined_output)


def parse_args() -> list[str]:
    parser = argparse.ArgumentParser(
        description="""Spits out contents of files matching glob patterns. Useful for LLM context.
Example usage: scripts/context.py 'app/routers/tools/balance_sheet/*.py' 'app/dtos/tools/balance_sheet/*.py' 'docs/tools/balance-sheet/*.md' 'docs/tools/README.md'
"""
    )
    parser.add_argument(
        "patterns",
        nargs="+",
        help="Glob patterns to include (e.g., 'app/models/*' '*.py' 'docs/**/*').",
    )

    args = parser.parse_args()
    return args.patterns


def main() -> None:
    patterns = parse_args()
    root_path = Path(".")

    # Load .gitignore if it exists, otherwise use a dummy filter
    gitignore_file = root_path / ".gitignore"
    if gitignore_file.exists():
        gitignore_matches = parse_gitignore(str(gitignore_file))
    else:

        def gitignore_matches(file_path) -> bool:
            return False

    full_output = process_project(
        root_path=root_path,
        gitignore_matches=gitignore_matches,
        patterns=patterns,
    )

    if full_output:
        print(full_output)
    else:
        print_in_stderr("No files matched the provided patterns.")


if __name__ == "__main__":
    main()
