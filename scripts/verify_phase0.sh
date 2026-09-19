#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
wolframscript_command="$(resolve_wolframscript)"
cd -- "$repository_root"

generated=(
    audit/source-manifest.json
    audit/source-manifest.csv
    audit/SHA256SUMS
    audit/audit-ledger.md
    audit/wolfram-structure.json
    audit/structural-audit.json
)
existing=()
for path in "${generated[@]}"; do
    [[ -f "$path" ]] && existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase0-verify-backup-bash.log -- \
        python scripts/backup_files.py "${existing[@]}"
fi

"$script_dir/run_logged.sh" logs/phase0-verify-tests-bash.log -- \
    python -m unittest discover -s tests -v
"$script_dir/run_logged.sh" logs/phase0-verify-manifest-bash.log -- \
    python scripts/build_source_manifest.py
"$script_dir/run_logged.sh" logs/phase0-verify-wolfram-bash.log -- \
    "$wolframscript_command" -file scripts/audit_wolfram.wls -- \
    audit/source-manifest.json audit/wolfram-structure.json
"$script_dir/run_logged.sh" logs/phase0-verify-structural-bash.log -- \
    python scripts/build_structural_audit.py
"$script_dir/run_logged.sh" logs/phase0-verify-check-bash.log -- \
    python scripts/check_phase0.py

printf '%s\n' 'phase0_verification=OK'