#!/usr/bin/env bash
set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source utility functions
source "$SCRIPT_DIR/utils.sh"

# Parse arguments
parse_args "$@"

# Start the server
run_with_env uv run uvicorn app.main:app --host 0.0.0.0 --reload --reload-include=.env
