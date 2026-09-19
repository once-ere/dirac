#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_COMMAND="${PYTHON_COMMAND:-python}"

exec "$PYTHON_COMMAND" "$SCRIPT_DIR/backup_files.py" "$@"