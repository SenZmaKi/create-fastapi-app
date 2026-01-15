#!/usr/bin/env bash
set -eo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source utility functions
source "$SCRIPT_DIR/utils.sh"

# Load environment variables (respects manual args)
load_env

# Create the database
uv run python -m scripts.db.create