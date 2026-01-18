#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

load_env

INIT_MIGRATIONS=false

# Detect --init_migrations flag
for arg in "$@"; do
  case "$arg" in
    --init_migrations)
      INIT_MIGRATIONS=true
      ;;
  esac
done

# Drop the database
uv run python -m scripts.db.drop "$@"

# Create the database
uv run python -m scripts.db.create "$@"

# Run migrations or initialize migrations
if [ "$INIT_MIGRATIONS" = true ]; then
  echo "Reinitializing migrations"
  VERSIONS_DIR="$SCRIPT_DIR/../alembic/versions"

  rm -rf "$VERSIONS_DIR"/*

  uv run alembic revision --autogenerate -m "Initial migration"
else
  bash "$SCRIPT_DIR/migrate_db.sh" "$@"
fi
