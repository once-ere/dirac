#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
wolframscript_command="$(resolve_wolframscript)"
cd -- "$repository_root"

artifact_path="artifacts/exact/cl44-seed.json"
repeat_path="build/phase1/cl44-seed-repeat.json"

if [[ -f "$artifact_path" ]]; then
    "$script_dir/run_logged.sh" logs/phase1-backup-generated-seed-bash.log -- \
        python scripts/backup_files.py "$artifact_path"
fi

mkdir -p -- "$(dirname -- "$repeat_path")"
"$script_dir/run_logged.sh" logs/phase1-cl44-seed-bash.log -- \
    "$wolframscript_command" -file scripts/verify_cl44.wls -- "$artifact_path"
"$script_dir/run_logged.sh" logs/phase1-cl44-seed-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/verify_cl44.wls -- "$repeat_path"
"$script_dir/run_logged.sh" logs/phase1-cl44-independent-bash.log -- \
    python scripts/check_cl44_fixture.py
"$script_dir/run_logged.sh" logs/phase1-python-tests-bash.log -- \
    python -m unittest discover -s tests -v

artifact_hash="$(sha256sum "$artifact_path" | cut -d' ' -f1)"
repeat_hash="$(sha256sum "$repeat_path" | cut -d' ' -f1)"
if [[ "$artifact_hash" != "$repeat_hash" ]]; then
    printf '%s\n' 'ERROR: repeated seed generation changed bytes'
    exit 1
fi

printf 'cl44_seed_sha256=%s\n' "$artifact_hash"
printf '%s\n' 'phase1_seed_verification=OK'