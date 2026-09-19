#!/usr/bin/env bash
set -euo pipefail

if (($# < 2)); then
    echo "usage: $0 LOG_PATH [--] COMMAND [ARG ...]" >&2
    exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
log_path="$1"
shift
if [[ "${1:-}" == "--" ]]; then
    shift
fi
if (($# == 0)); then
    echo "missing command" >&2
    exit 2
fi

if [[ "$log_path" != /* ]]; then
    log_path="$repository_root/$log_path"
fi
mkdir -p -- "$(dirname -- "$log_path")"

{
    printf 'started_utc=%s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    printf 'repository=%s\n' "$repository_root"
    printf 'command=' 
    printf '%q ' "$@"
    printf '\n'
} >"$log_path"

set +e
"$@" 2>&1 | tee -a "$log_path"
command_exit_code=${PIPESTATUS[0]}
set -e

{
    printf 'finished_utc=%s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    printf 'exit_code=%d\n' "$command_exit_code"
} >>"$log_path"

exit "$command_exit_code"