#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="$(mktemp)"
LOG="$(mktemp)"

trap 'rm -f "$REPORT" "$LOG"' EXIT

set +e
uv run --directory "$PROJECT_ROOT/backend" \
  pytest --junitxml="$REPORT" "$@" \
  >"$LOG" 2>&1
status=$?
set -e

if [[ $status -ne 0 ]]; then
  cat "$LOG"
fi

read -r passed total < <(
  python3 "$PROJECT_ROOT/scripts/count_tests.py" "$REPORT"
)

echo "TESTS: $passed/$total"

exit "$status"
