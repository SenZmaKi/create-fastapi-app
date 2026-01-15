#!/usr/bin/env bash
set -eo pipefail

DEPLOYMENT_ENVIRONMENT=testing uv run pytest $@