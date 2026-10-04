#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

exec uv run --directory "$PROJECT_ROOT/backend" \
  uvicorn backend.server:app \
  --app-dir src \
  --reload \
  "$@"
