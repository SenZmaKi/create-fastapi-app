#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

RESET_MIGRATIONS=false

# Extend parse_args to detect --init_migrations
for arg in "$@"; do
  case "$arg" in
    --reset-migrations)
      RESET_MIGRATIONS=true
      ;;
  esac
done

parse_args "$@"

# Drop the database
run_with_env uv run python -m scripts.db.drop "${ARGS[@]}"


# Reset migrations
if [ "$RESET_MIGRATIONS" = true ]; then
  echo "Reinitializing migrations"
  VERSIONS_DIR="$SCRIPT_DIR/../alembic/versions"

  rm -rf "$VERSIONS_DIR"/*

  run_with_env uv run alembic revision --autogenerate -m "Initial migration"
fi


# Create the database
run_with_env uv run python -m scripts.db.setup "${ARGS[@]}"
