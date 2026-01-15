#!/usr/bin/env bash
set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source utility functions
source "$SCRIPT_DIR/utils.sh"

# Load environment variables (respects manual args)
load_env

# Start the server
# If DEPLOYMENT_ENVIRONMENT=production or RUNNING_IN_DOCKER=true, run the app directly, will use DEPLOYMENT_ENVIRONMENT variables to check for reload
if [[ "${DEPLOYMENT_ENVIRONMENT:-}" == "production" || "${RUNNING_IN_DOCKER:-}" == "true" ]]; then
    .venv/bin/python -m app
else
    # HACK: Configuring reload in params in app/main.py does not seem to work, we have to invoke uvicorn directly with the args
	uv run uvicorn app.main:app --host 0.0.0.0 --reload --reload-include=.env
fi
