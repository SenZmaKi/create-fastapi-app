from typing import Literal


def print_colored(
    text: str, color: Literal["green", "blue", "red", "reset"] = "blue"
) -> None:
    """Print colored text to console."""
    colors = {
        "green": "\033[0;32m",
        "blue": "\033[0;34m",
        "red": "\033[0;31m",
        "reset": "\033[0m",
    }
    color_code = colors[color]
    print(f"{color_code}{text}{colors['reset']}")
