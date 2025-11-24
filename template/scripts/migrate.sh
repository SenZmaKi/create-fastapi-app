#!/usr/bin/env bash
set -e 

uv run alembic upgrade head
