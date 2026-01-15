#!/usr/bin/env bash
set -eo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source utility functions
source "$SCRIPT_DIR/utils.sh"

# Parse arguments
parse_args "$@"

# Run migrations
run_with_env uv run alembic upgrade head

