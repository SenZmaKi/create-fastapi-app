set -e

ENV=testing uv run uvicorn app.main:app --host 0.0.0.0 --reload --reload-include=.env $@
